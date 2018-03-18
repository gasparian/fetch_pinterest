from fetch_pinterest import *
import config

if __name__ == "__main__":

    getter = PinterestAPI(path=config.folder_path, access_token=config.access_token, timeout=config.timeout)
    for board_id in config.board_ids:
        getter.get_pins_from_board(board_id)