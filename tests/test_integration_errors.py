"""
Tests d'intégration — Pages d'erreur HTTP.
"""
import pytest


# Fixtures app et client supprimées — définies dans conftest.py
# Note : PROPAGATE_EXCEPTIONS doit être False pour que les gestionnaires d'erreur s'activent


@pytest.fixture
def error_client(app):
    """Client configuré pour laisser les gestionnaires d'erreur fonctionner"""
    app.config['PROPAGATE_EXCEPTIONS'] = False
    return app.test_client()


class TestErrorPages:
    """Tests des pages d'erreur"""

    def test_404_route_inexistante(self, error_client):
        """Une route inconnue retourne une page 404"""
        response = error_client.get('/route-inexistante-xyz')
        assert response.status_code == 404
        assert b'404' in response.data

    def test_404_via_route_test(self, error_client):
        """La route /test/404 retourne bien une page 404"""
        response = error_client.get('/test/404')
        assert response.status_code == 404
        assert b'404' in response.data

    def test_500_via_route_test(self, error_client):
        """La route /test/500 retourne bien une page 500"""
        response = error_client.get('/test/500')
        assert response.status_code == 500
        assert b'500' in response.data or b'Erreur serveur' in response.data

    def test_403_via_route_test(self, error_client):
        """La route /test/403 retourne bien une page 403"""
        response = error_client.get('/test/403')
        assert response.status_code == 403
        assert b'403' in response.data

    def test_400_via_route_test(self, error_client):
        """La route /test/400 retourne bien une page 400"""
        response = error_client.get('/test/400')
        assert response.status_code == 400
        assert b'400' in response.data

    def test_pages_erreur_ont_bouton_retour(self, error_client):
        """Toutes les pages d'erreur contiennent un bouton de retour"""
        response = error_client.get('/test/404')
        assert b'Retour' in response.data

    def test_pages_erreur_contiennent_du_html(self, error_client):
        """Les pages d'erreur retournent du HTML substantiel"""
        routes = [
            ('/test/404', 404),
            ('/test/403', 403),
            ('/test/400', 400),
            ('/test/500', 500),
        ]
        for route, expected_code in routes:
            response = error_client.get(route)
            assert response.status_code == expected_code
            assert len(response.data) > 100, \
                f"{route} retourne trop peu de contenu ({len(response.data)} octets)"