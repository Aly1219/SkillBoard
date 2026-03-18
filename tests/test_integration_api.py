"""
Tests d'intégration — API REST étendue.
⚠️ Ces tests sont en attente d'implémentation de l'API /api/v1/...
   Tous les tests sont skippés pour ne pas polluer les résultats pytest.
"""
import pytest


pytestmark = pytest.mark.skip(reason="API /api/v1/ non encore implémentée")


class TestAPICompetencesBasic:

    def test_get_competence_by_id(self, app, client):
        pass

    def test_update_competence_via_api(self, app, client):
        pass

    def test_delete_competence_via_api(self, app, client):
        pass


class TestAPIAuth:

    def test_register_via_api(self, app, client):
        pass

    def test_login_via_api(self, app, client):
        pass

    def test_login_invalid_credentials_via_api(self, app, client):
        pass


class TestAPIErrors:

    def test_get_nonexistent_competence(self, client):
        pass

    def test_api_documentation_accessible(self, client):
        pass