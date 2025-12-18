def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_valid_login(client, auth):
    response = auth.login()
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_invalid_login_credentials(client, auth):
    response = auth.login(username='wrong', password='wrong')
    assert response.status_code == 200
    assert b'Login Unsuccessful' in response.data

def test_invalid_access_code(client, auth):
    response = auth.login(access_code='INVALID')
    assert response.status_code == 200
    assert b'Invalid Access Code' in response.data

def test_logout(client, auth):
    auth.login()
    response = auth.logout()
    assert response.status_code == 200
    # On logout, we redirect to login
    assert b'Login' in response.data
