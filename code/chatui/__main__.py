from chatui import pages
import os


if __name__ == "__main__":
    
    proxy_prefix = os.environ.get("PROXY_PREFIX")
    blocks = pages.converse.build_page()
    blocks.queue(max_size=10)
    blocks.launch(server_name="0.0.0.0", server_port=8080, root_path=proxy_prefix)
    