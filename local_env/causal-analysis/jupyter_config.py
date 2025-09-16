# Jupyter Notebook configuration
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.allow_root = True
c.NotebookApp.open_browser = False

# Disable authentication
c.NotebookApp.token = ''
c.NotebookApp.password = ''

# Allow all origins (useful for development)
c.NotebookApp.allow_origin = '*'
c.NotebookApp.disable_check_xsrf = True

# Additional settings for better experience
c.NotebookApp.allow_remote_access = True
c.NotebookApp.allow_password_change = False