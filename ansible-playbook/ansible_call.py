
import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C
import yaml


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        if result.task_name == "Gathering Facts":
            return
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


if __name__ == '__main__':
    context.CLIARGS = ImmutableDict(connection='smart', forks=10, become=None,
                                    become_method=None, become_user=None, check=False, diff=False, verbosity=0,
                                    private_key_file="~/.ssh/id_rsa")

    loader = DataLoader()
    passwords = dict(vault_pass='')

    inventory = InventoryManager(loader=loader, sources='./hosts')

    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # host_list = ['121.4.55.33']
    # play_source = dict(
    #     name="Ansible Play",
    #     hosts=host_list,
    #     gather_facts='no',
    #     tasks=[
    #         dict(action=dict(module='shell', args='ls'), register='shell_out'),
    #         dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}'))),
    #         dict(action=dict(module='command', args=dict(cmd='/usr/bin/uptime'))),
    #     ]
    # )

    play_source = []
    with open("./mysql.yml") as f:
        data = yaml.load(f, yaml.SafeLoader)
        if isinstance(data, list):
            play_source.extend(data)
        else:
            play_source.append(data)
    print(play_source[0])
    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided in play_source
    play = Play().load(play_source[0], variable_manager=variable_manager, loader=loader)

    results_callback = ResultCallback()
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
        stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
    )


    # Actually run it
    try:
        result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        tqm.cleanup()
        if loader:
            loader.cleanup_all_tmp_files()

    # play_source = []
    # with open("./mysql.yml") as f:
    #     data = yaml.load(f, yaml.SafeLoader)
    #     if isinstance(data, list):
    #         play_source.extend(data)
    #     else:
    #         play_source.append(data)

    # for play_book in play_source:
    #     play = Play().load(play_book, variable_manager=variable_manager, loader=loader)
    #     results_callback = ResultCallback()
    #     tqm = None
    #     try:
    #         tqm = TaskQueueManager(
    #             inventory=inventory,
    #             variable_manager=variable_manager,
    #             loader=loader,
    #             passwords=passwords,
    #             stdout_callback=results_callback
    #         )

    #         result = tqm.run(play)
    #     finally:
    #         if tqm is not None:
    #             tqm.cleanup()
    #         shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)