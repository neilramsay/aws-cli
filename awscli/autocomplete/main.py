# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


# This is the main entry point for auto-completion.  This is imported
# everytime a user hits <TAB>.  Try to avoid any expensive module level
# work or really heavyweight imports.  Prefer to lazy load as much as possible.
from typing import TYPE_CHECKING

from awscli.autocomplete import completer, custom, filters, parser, serverside
from awscli.autocomplete.local import basic, fetcher, model

if TYPE_CHECKING:
    from awscli.autocomplete.completer import AutoCompleter, BaseCompleter
    from awscli.autocomplete.filters import Filter
    from awscli.clidriver import CLIDriver


def create_autocompleter(
    index_filename: str | None = None,
    custom_completers: list["BaseCompleter"] | None = None,
    driver: "CLIDriver | None" = None,
    response_filter: "Filter | None" = None,
) -> "AutoCompleter":
    """
    Create an autocompleter to orchestrate shell completion request
    and registered completers.
    
    :param index_filename: path to the precompiled service/command database
    :type index_filename: str | None
    :param custom_completers: custom completers to be appended to standard completers
    :type custom_completers: list[BaseCompleter] | None
    :param driver: AWS CLI handler
    :type driver: CLIDriver | None
    :param response_filter: Filter completion responses before returning to shell
    :type response_filter: Filter | None
    :return: Shell Autocompleter
    :rtype: AutoCompleter
    """

    if response_filter is None:
        response_filter = filters.startswith_filter
    if custom_completers is None:
        custom_completers = custom.get_custom_completers()
    index = model.ModelIndex(index_filename)
    cli_parser = parser.CLIParser(index)
    cli_driver_fetcher = None
    if driver is not None:
        cli_driver_fetcher = fetcher.CliDriverFetcher(driver)
    completers = [
        basic.RegionCompleter(response_filter=response_filter),
        basic.ProfileCompleter(response_filter=response_filter),
        basic.ModelIndexCompleter(
            index, cli_driver_fetcher, response_filter=response_filter
        ),
        basic.FilePathCompleter(response_filter=response_filter),
        serverside.create_server_side_completer(
            index_filename, response_filter=response_filter
        ),
        basic.ShorthandCompleter(
            cli_driver_fetcher, response_filter=response_filter
        ),
        basic.QueryCompleter(
            cli_driver_fetcher, response_filter=response_filter
        ),
    ] + custom_completers
    cli_completer = completer.AutoCompleter(cli_parser, completers)
    return cli_completer


def autocomplete(command_line: str, position: int | None = None) -> None:
    """
    Write shell completion results to standard out for the provided
    command line and position

    :param command_line: command line to perform completion on
    :type command_line: str
    :param position: position within command line to perform completion on
    :type position: int | None
    """
    completer = create_autocompleter()
    results = completer.autocomplete(command_line, position)
    print("\n".join([result.name for result in results]))
