from Network import server

server.core.getCARDS()

if server.core.DEV():
    match server.core.cleanstr(input("Would you like to `host` or `join` a party? ")):
        case "host": server.host(
            input("Choose your username: "),
            server.core.ifelse(server.core.cleanstr(input("Would you like to localhost [yes/no]? ")) == "yes",
                "127.0.0.1",
                server.net.get_ip()
            )
        )
        case "join": server.join(
            input("Choose your username: "),
            input("Enter your host IP: ")
        )
        case _: print("Unreconized action. Terminating process.")
else:
    from main import main
    main()
