from hca_util.local_state import get_local_state, set_local_state


class CmdDir:

    @staticmethod
    def run():
        local_state = get_local_state()

        selected_dir = None
        if local_state:
            selected_dir = local_state.selected_dir

        if not selected_dir:
            print('No directory selected')
            return

        print(str(local_state))

    @staticmethod
    def clear():
        local_state = get_local_state()
        local_state.unselect_dir()
        set_local_state(local_state)

        print(str(local_state))
