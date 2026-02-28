"""
Tests unitaires pour les utilitaires
"""
import pytest
import os
import sys
from app.utils import resource_path


class TestResourcePath:
    """Tests pour la fonction resource_path"""
    
    def test_resource_path_dev(self):
        """✅ Test resource_path en mode développement"""
        # En dev, _MEIPASS n'existe pas
        path = resource_path("templates")
        assert "templates" in path
        assert os.path.isabs(path)
    
    def test_resource_path_returns_absolute(self):
        """✅ Test que resource_path retourne un chemin absolu"""
        path = resource_path("app")
        assert os.path.isabs(path)
    
    def test_resource_path_with_subdir(self):
        """✅ Test resource_path avec sous-dossiers"""
        path = resource_path("app/templates/index.html")
        assert "app" in path
        assert "templates" in path
        assert "index.html" in path
        assert os.path.isabs(path)