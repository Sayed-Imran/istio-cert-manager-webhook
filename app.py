import uvicorn
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:     %(message)s'
)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--certfile', 
                        help='Path to the TLS certificate file')
    parser.add_argument('--keyfile', 
                        help='Path to the TLS key file')
    parser.add_argument('--port', 
                        type=int, 
                        default=8000, 
                        help='Port to run the server on (default: 8000)')
    parser.add_argument('--host', 
                        default='0.0.0.0', 
                        help='Host interface to bind to (default: 0.0.0.0)')

    args = parser.parse_args()

    config = {
        "app": "main:app",
        "host": args.host,
        "port": args.port,
    }

    if args.certfile and args.keyfile:
        config["ssl_certfile"] = args.certfile
        config["ssl_keyfile"] = args.keyfile
        logging.info(f"Running with TLS using certificate: {args.certfile}")
    else:
        logging.warning("Running without TLS")

    uvicorn.run(**config)

if __name__ == "__main__":
    main()
