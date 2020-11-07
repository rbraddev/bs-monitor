# BS-Monitor

Files required:

    * proxies.txt - format: ip:username:password
    * monitors.yml

Files for testing:

    * test_proxy.txt - just include one working proxy, same format as proxies.txt


Basic usage:

    from monitor.monitor import Monitor

    monitor = Monitor()
    monitor.run()