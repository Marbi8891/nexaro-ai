def test_stats_requiere_auth(client):
    res = client.get("/api/stats")
    assert res.status_code == 401


def test_stats_estructura(client, auth_headers):
    res = client.get("/api/stats", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "conversion_rate" in data
    assert "by_status" in data
    assert "by_source" in data
    assert "daily_last_7d" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["conversion_rate"], float)
    assert isinstance(data["by_status"], dict)
    assert isinstance(data["daily_last_7d"], list)


def test_stats_con_leads(client, auth_headers, sample_lead):
    """Con al menos un lead, total debe ser >= 1 y new debe existir en by_status."""
    res = client.get("/api/stats", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert "new" in data["by_status"]
    assert data["by_status"]["new"] >= 1


def test_stats_conversion_rate_rango(client, auth_headers):
    """La tasa de conversión debe estar entre 0 y 100."""
    res = client.get("/api/stats", headers=auth_headers)
    data = res.json()
    assert 0.0 <= data["conversion_rate"] <= 100.0


def test_stats_daily_estructura(client, auth_headers, sample_lead):
    """Cada entrada de daily_last_7d debe tener 'day' y 'count'."""
    res = client.get("/api/stats", headers=auth_headers)
    daily = res.json()["daily_last_7d"]
    for entry in daily:
        assert "day" in entry
        assert "count" in entry
        assert isinstance(entry["count"], int)
