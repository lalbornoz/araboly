#!/bin/sh

usage() {
	echo "usage: ${0} [-h]" >&2;
	echo "       -h.......: show this screen" >&2;
};

main() {
	local	_log_dname="checkOutput" _log_pname="" _savefile_fname="";
	while getopts h _opt; do
	case "${_opt}" in
	h) usage; exit 0; ;;
	*) usage; exit 1; ;;
	esac; done;
	if [ -d "${_log_dname}" ]; then
		echo "error: refuse to overwrite directory ${_log_dname}/";
		exit 2;
	else
		mkdir "${_log_dname}";
	fi;
	for _savefile_pname in $(find assets/savefiles -name *.yml -not -name last.yml); do
		_savefile_fname="${_savefile_pname##*/}";
		_log_pname="${_log_dname}/${_savefile_fname}";
		printf "${_savefile_fname}: ";
		if ./ArabolyDebugger.py -f "${_savefile_pname}" > "${_log_pname}" 2>&1; then
			printf "[32mPASSED[0m\n";
			rm -f "${_log_pname}";
		else
			printf "[31mFAILED[0m\n";
		fi;
	done;
};

set -o errexit -o noglob;
main "${@}";

# vim:foldmethod=marker sw=8 ts=8 tw=120
