import h2o

h2o.init()

print("H2O started successfully.")
h2o.cluster().show_status()

h2o.cluster().shutdown()
