import json
import os
from typing import Dict, List, Optional, Any
import asyncio
from threading import Lock

class ConfigManager:
    """Gestionnaire de configuration pour le bot Discord"""
    
    DEFAULT_CONFIG = {
        "prefix": "!",
        "command_names": {
            "play": "play",
            "queue": "queue",
            "skip": "skip",
            "pause": "pause",
            "resume": "resume",
            "stop": "stop",
            "clear": "clear",
            "remove": "remove",
            "nowplaying": "nowplaying",
            "loop": "loop",
            "volume": "volume",
            "leave": "leave",
            "ping": "ping"
        },
        "command_aliases": {
            "play": ["p"],
            "queue": ["q", "list"],
            "skip": ["s"],
            "pause": [],
            "resume": [],
            "stop": [],
            "clear": [],
            "remove": [],
            "nowplaying": ["np", "now"],
            "loop": [],
            "volume": ["vol"],
            "leave": ["disconnect", "dc"],
            "ping": []
        },
        "permissions": {
            "play": [],
            "queue": [],
            "skip": [],
            "pause": [],
            "resume": [],
            "stop": [],
            "clear": [],
            "remove": [],
            "nowplaying": [],
            "loop": [],
            "volume": [],
            "leave": [],
            "ping": []
        },
        "default_settings": {
            "volume": 50,
            "loop_mode": False,
            "auto_disconnect": False,
            "auto_disconnect_delay": 300
        }
    }
    
    def __init__(self, config_file: str = "configs/guild_configs.json"):
        self.config_file = config_file
        self.configs: Dict[int, Dict] = {}
        self.lock = Lock()
        self._ensure_config_dir()
        self.load_configs()
    
    def _ensure_config_dir(self):
        """Crée le dossier de configuration s'il n'existe pas"""
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
    def load_configs(self):
        """Charge les configurations depuis le fichier JSON"""
        with self.lock:
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convertir les clés de string à int
                        self.configs = {int(k): v for k, v in data.items()}
                    print(f"✅ Configurations chargées pour {len(self.configs)} serveur(s)")
                except Exception as e:
                    print(f"❌ Erreur lors du chargement de la configuration : {e}")
                    self.configs = {}
            else:
                print("ℹ️ Aucun fichier de configuration trouvé, démarrage avec configuration par défaut")
                self.configs = {}
    
    def save_configs(self):
        """Sauvegarde les configurations dans le fichier JSON"""
        with self.lock:
            return self._save_configs_internal()
    
    def _save_configs_internal(self):
        """Méthode interne de sauvegarde sans lock (doit être appelée dans un contexte lock)"""
        try:
            # Convertir les clés de int à string pour JSON
            data = {str(k): v for k, v in self.configs.items()}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de la configuration : {e}")
            return False
    
    def get_guild_config(self, guild_id: int) -> Dict:
        """Récupère la configuration d'un serveur (ou crée une config par défaut)"""
        with self.lock:
            if guild_id not in self.configs:
                self.configs[guild_id] = self._create_default_config()
                self._save_configs_internal()
            return self.configs[guild_id].copy()
    
    def _create_default_config(self) -> Dict:
        """Crée une copie profonde de la configuration par défaut"""
        return json.loads(json.dumps(self.DEFAULT_CONFIG))
    
    def get_prefix(self, guild_id: int) -> str:
        """Récupère le préfixe d'un serveur"""
        config = self.get_guild_config(guild_id)
        return config.get("prefix", "!")
    
    def set_prefix(self, guild_id: int, prefix: str) -> bool:
        """Définit le préfixe d'un serveur"""
        if not prefix or len(prefix) > 3:
            return False
        
        with self.lock:
            if guild_id not in self.configs:
                self.configs[guild_id] = self._create_default_config()
            self.configs[guild_id]["prefix"] = prefix
            return self._save_configs_internal()
    
    def get_command_name(self, guild_id: int, original_name: str) -> str:
        """Récupère le nom personnalisé d'une commande"""
        config = self.get_guild_config(guild_id)
        return config.get("command_names", {}).get(original_name, original_name)
    
    def set_command_name(self, guild_id: int, original_name: str, new_name: str) -> bool:
        """Définit le nom personnalisé d'une commande"""
        if not new_name or not new_name.replace("_", "").isalnum():
            return False
        
        with self.lock:
            if guild_id not in self.configs:
                self.configs[guild_id] = self._create_default_config()
            
            if "command_names" not in self.configs[guild_id]:
                self.configs[guild_id]["command_names"] = {}
            
            self.configs[guild_id]["command_names"][original_name] = new_name
            return self._save_configs_internal()
    
    def get_command_aliases(self, guild_id: int, original_name: str) -> List[str]:
        """Récupère les alias d'une commande"""
        config = self.get_guild_config(guild_id)
        return config.get("command_aliases", {}).get(original_name, [])
    
    def add_command_alias(self, guild_id: int, original_name: str, alias: str) -> bool:
        """Ajoute un alias à une commande"""
        if not alias or not alias.replace("_", "").isalnum():
            return False
        
        with self.lock:
            if guild_id not in self.configs:
                self.configs[guild_id] = self._create_default_config()
            
            if "command_aliases" not in self.configs[guild_id]:
                self.configs[guild_id]["command_aliases"] = {}
            
            if original_name not in self.configs[guild_id]["command_aliases"]:
                self.configs[guild_id]["command_aliases"][original_name] = []
            
            if alias not in self.configs[guild_id]["command_aliases"][original_name]:
                self.configs[guild_id]["command_aliases"][original_name].append(alias)
                return self._save_configs_internal()
            
            return False
    
    def remove_command_alias(self, guild_id: int, original_name: str, alias: str) -> bool:
        """Retire un alias d'une commande"""
        with self.lock:
            if guild_id not in self.configs:
                return False
            
            aliases = self.configs[guild_id].get("command_aliases", {}).get(original_name, [])
            if alias in aliases:
                aliases.remove(alias)
                return self._save_configs_internal()
            
            return False
    
    def get_command_permissions(self, guild_id: int, original_name: str) -> List[str]:
        """Récupère les permissions d'une commande (noms de rôles)"""
        config = self.get_guild_config(guild_id)
        return config.get("permissions", {}).get(original_name, [])
    
    def set_command_permissions(self, guild_id: int, original_name: str, roles: List[str]) -> bool:
        """Définit les permissions d'une commande"""
        with self.lock:
            if guild_id not in self.configs:
                self.configs[guild_id] = self._create_default_config()
            
            if "permissions" not in self.configs[guild_id]:
                self.configs[guild_id]["permissions"] = {}
            
            self.configs[guild_id]["permissions"][original_name] = roles
            return self._save_configs_internal()
    
    def clear_command_permissions(self, guild_id: int, original_name: str) -> bool:
        """Retire toutes les restrictions de permission d'une commande"""
        return self.set_command_permissions(guild_id, original_name, [])
    
    def get_default_setting(self, guild_id: int, setting_name: str) -> Any:
        """Récupère un paramètre par défaut"""
        config = self.get_guild_config(guild_id)
        return config.get("default_settings", {}).get(setting_name)
    
    def set_default_setting(self, guild_id: int, setting_name: str, value: Any) -> bool:
        """Définit un paramètre par défaut"""
        with self.lock:
            if guild_id not in self.configs:
                self.configs[guild_id] = self._create_default_config()
            
            if "default_settings" not in self.configs[guild_id]:
                self.configs[guild_id]["default_settings"] = {}
            
            self.configs[guild_id]["default_settings"][setting_name] = value
            return self._save_configs_internal()
    
    def reset_guild_config(self, guild_id: int) -> bool:
        """Réinitialise la configuration d'un serveur"""
        with self.lock:
            self.configs[guild_id] = self._create_default_config()
            return self._save_configs_internal()
    
    def export_guild_config(self, guild_id: int) -> str:
        """Exporte la configuration d'un serveur en JSON"""
        config = self.get_guild_config(guild_id)
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def import_guild_config(self, guild_id: int, json_str: str) -> bool:
        """Importe une configuration depuis JSON"""
        try:
            config = json.loads(json_str)
            # Validation basique
            if not isinstance(config, dict):
                return False
            
            with self.lock:
                self.configs[guild_id] = config
                return self._save_configs_internal()
        except Exception as e:
            print(f"❌ Erreur lors de l'import : {e}")
            return False
    
    def has_permission(self, guild, user, original_command_name: str) -> bool:
        """Vérifie si un utilisateur a la permission d'utiliser une commande"""
        required_roles = self.get_command_permissions(guild.id, original_command_name)
        
        # Si aucune restriction, tout le monde peut utiliser
        if not required_roles:
            return True
        
        # Vérifier si l'utilisateur a un des rôles requis
        user_role_names = [role.name for role in user.roles]
        return any(role in user_role_names for role in required_roles)

