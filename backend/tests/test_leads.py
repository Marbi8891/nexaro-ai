import pytest


VALID_LEAD = {
    "name": "María García",
    "email": "maria@empresa.com",
    "phone": "612345678",
    "company": "Clínica Dental García",
    "message": "Quiero saber más sobre automatización de citas",
    "source": "web",
}


# ── Crear lead ──────────────────────────────────────────────────────────────

class TestCrearLead:
    def test_crear_lead_valido(self, client):
        res = client.post("/api/leads", json=VALID_LEAD)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == VALID_LEAD["name"]
        assert data["email"] == VALID_LEAD["email"]
        assert data["status"] == "new"
        assert data["source"] == "web"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_crear_lead_minimo(self, client):
        """Solo campos obligatorios."""
        res = client.post("/api/leads", json={
            "name": "Juan",
            "email": "juan@test.com",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["phone"] is None
        assert data["company"] is None

    def test_crear_lead_sin_nombre(self, client):
        payload = {**VALID_LEAD, "name": ""}
        res = client.post("/api/leads", json=payload)
        assert res.status_code == 422

    def test_crear_lead_email_invalido(self, client):
        payload = {**VALID_LEAD, "email": "no-es-un-email", "phone": "600000002"}
        res = client.post("/api/leads", json=payload)
        assert res.status_code == 422

    def test_crear_lead_sin_email(self, client):
        payload = {k: v for k, v in VALID_LEAD.items() if k != "email"}
        res = client.post("/api/leads", json=payload)
        assert res.status_code == 422

    def test_honeypot_activa_rechazo(self, client):
        """Si el campo honeypot tiene valor, debe rechazarse silenciosamente."""
        res = client.post("/api/leads?website=relleno", json=VALID_LEAD)
        assert res.status_code == 422

    def test_lead_duplicado_mismo_email_24h(self, client):
        """Mismo email dos veces en menos de 24h debe devolver 409."""
        payload = {**VALID_LEAD, "email": "dup@test.com", "phone": "600000010"}
        res1 = client.post("/api/leads", json=payload)
        assert res1.status_code == 201
        res2 = client.post("/api/leads", json=payload)
        assert res2.status_code == 409

    def test_lead_emails_distintos_no_duplica(self, client):
        res1 = client.post("/api/leads", json={**VALID_LEAD, "email": "a@test.com", "phone": "600000020"})
        res2 = client.post("/api/leads", json={**VALID_LEAD, "email": "b@test.com", "phone": "600000021"})
        assert res1.status_code == 201
        assert res2.status_code == 201

    def test_injection_sql_rechazado(self, client):
        payload = {**VALID_LEAD, "email": "inj@test.com", "name": "'; DROP TABLE leads; --", "phone": "600000030"}
        res = client.post("/api/leads", json=payload)
        assert res.status_code == 400

    def test_fuente_invalida(self, client):
        payload = {**VALID_LEAD, "email": "src@test.com", "source": "tiktok", "phone": "600000031"}
        res = client.post("/api/leads", json=payload)
        assert res.status_code == 422


# ── Listar leads ────────────────────────────────────────────────────────────

class TestListarLeads:
    def test_listar_requiere_auth(self, client):
        res = client.get("/api/leads")
        assert res.status_code == 401

    def test_listar_con_token(self, client, auth_headers, sample_lead):
        res = client.get("/api/leads", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 1

    def test_listar_filtro_status(self, client, auth_headers, sample_lead):
        res = client.get("/api/leads?status=new", headers=auth_headers)
        assert res.status_code == 200
        items = res.json()["items"]
        for item in items:
            assert item["status"] == "new"

    def test_listar_filtro_status_invalido(self, client, auth_headers):
        res = client.get("/api/leads?status=fantasma", headers=auth_headers)
        assert res.status_code == 422

    def test_listar_paginacion(self, client, auth_headers, sample_lead):
        res = client.get("/api/leads?skip=0&limit=1", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()["items"]) <= 1

    def test_listar_busqueda(self, client, auth_headers, sample_lead):
        email_fragment = sample_lead["email"][:5]
        res = client.get(f"/api/leads?search={email_fragment}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["total"] >= 1

    def test_orden_created_at_desc(self, client, auth_headers):
        """Los leads más recientes deben aparecer primero."""
        for i in range(3):
            client.post("/api/leads", json={
                **VALID_LEAD,
                "email": f"orden{i}@test.com",
                "phone": f"60000004{i}",
            })
        res = client.get("/api/leads", headers=auth_headers)
        items = res.json()["items"]
        if len(items) >= 2:
            assert items[0]["created_at"] >= items[1]["created_at"]


# ── Detalle lead ────────────────────────────────────────────────────────────

class TestDetalleLead:
    def test_get_lead_existente(self, client, auth_headers, sample_lead):
        lead_id = sample_lead["id"]
        res = client.get(f"/api/leads/{lead_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["id"] == lead_id

    def test_get_lead_inexistente(self, client, auth_headers):
        res = client.get("/api/leads/99999", headers=auth_headers)
        assert res.status_code == 404

    def test_get_lead_requiere_auth(self, client, sample_lead):
        lead_id = sample_lead["id"]
        res = client.get(f"/api/leads/{lead_id}")
        assert res.status_code == 401


# ── Actualizar lead ─────────────────────────────────────────────────────────

class TestActualizarLead:
    def test_actualizar_status(self, client, auth_headers, sample_lead):
        lead_id = sample_lead["id"]
        res = client.patch(
            f"/api/leads/{lead_id}",
            json={"status": "contacted"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "contacted"

    def test_actualizar_notes(self, client, auth_headers, sample_lead):
        lead_id = sample_lead["id"]
        res = client.patch(
            f"/api/leads/{lead_id}",
            json={"notes": "Llamado el lunes, interesado en plan básico"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert "Llamado" in res.json()["notes"]

    def test_actualizar_status_y_notes(self, client, auth_headers, sample_lead):
        lead_id = sample_lead["id"]
        res = client.patch(
            f"/api/leads/{lead_id}",
            json={"status": "qualified", "notes": "Presupuesto enviado"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "qualified"
        assert "Presupuesto" in data["notes"]

    def test_actualizar_status_invalido(self, client, auth_headers, sample_lead):
        lead_id = sample_lead["id"]
        res = client.patch(
            f"/api/leads/{lead_id}",
            json={"status": "pendiente"},
            headers=auth_headers,
        )
        assert res.status_code == 422

    def test_actualizar_lead_inexistente(self, client, auth_headers):
        res = client.patch(
            "/api/leads/99999",
            json={"status": "contacted"},
            headers=auth_headers,
        )
        assert res.status_code == 404

    def test_actualizar_requiere_auth(self, client, sample_lead):
        lead_id = sample_lead["id"]
        res = client.patch(f"/api/leads/{lead_id}", json={"status": "contacted"})
        assert res.status_code == 401

    def test_patch_vacio_no_rompe(self, client, auth_headers, sample_lead):
        """PATCH con payload vacío no debe romper el lead."""
        lead_id = sample_lead["id"]
        res = client.patch(f"/api/leads/{lead_id}", json={}, headers=auth_headers)
        assert res.status_code == 200
