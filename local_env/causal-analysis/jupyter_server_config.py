# Jupyter Server configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False

# Disable all authentication
c.ServerApp.token = ""
c.ServerApp.password = ""
c.PasswordIdentityProvider.allow_password_change = False

# Security settings for development
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True
c.ServerApp.allow_remote_access = True

# Notebook settings
c.ServerApp.quit_button = False
c.ServerApp.disable_check_xsrf = True