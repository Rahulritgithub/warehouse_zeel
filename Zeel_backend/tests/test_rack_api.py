from Models.rack import Rack


def test_create_rack(client, db):
    response = client.post(
        "/api/v1/racks/add/",
        json={"rack_id": "RACK-A1", "location": "Warehouse-1"},
    )

    assert response.status_code == 201

    rack = db.query(Rack).filter_by(rack_id="RACK-A1").first()
    assert rack is not None
    assert rack.location == "Warehouse-1"
    print(response.json())
