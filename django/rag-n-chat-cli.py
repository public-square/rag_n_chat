#!./.venv/bin/python
"""
Example of using sub-parser, sub-commands and sub-sub-commands :-)
"""

from pathlib import Path
import environ
import os
import argparse
from common.utils import *

# Initialize environ
BASE_DIR = Path(__file__).resolve().parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, 'global', '.env'))


def ping(args):
    """
    Proof of life. Reverses a provided text string.
    """
    if not args.text:
        print('Please provide a text field in the request body')
        return

    input_text = args.text

    if not isinstance(input_text, str):
        print('Text field must be a string')
        return

    if len(input_text) > 1024:
        print('Text must not exceed 1024 characters')
        return

    reversed_text = input_text[::-1]

    print({
        'ping': input_text,
        'pong': reversed_text
    })

def repo_list(args):
    """
    List repositories for RAG
    """
    from common.repo.list import list_repositories

    repos = list_repositories()
    print(repos)

def repo_vectorize(args):
    """
    Vectorize repository
    """
    from common.repo.vectorize import vectorize_repository

    repo = args.repo
    if not repo:
        print('Please provide a repository owner/repo/branch')
        return

    vectorize_repository(repo)

def repo_delete(args):
    """
    Delete repository
    """
    from common.repo.delete import delete_repository

    repo = args.repo
    if not repo:
        print('Please provide a repository owner/repo/branch')
        return

    delete_repository(repo)

def chat_prompt(args):
    """
    Chat with LLM
    """
    from common.chat.prompt import process_chat_prompt
    prompt = args.prompt
    if not prompt:
        print('Please supply a prompt')
        return
    repo = args.repo
    context = args.context
    print (process_chat_prompt(prompt, repo, context))
    print('repo: ', repo)


if __name__ == '__main__':
    # root parser
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('--json', action='store_true', help='produce JSON output')

    # command sub-parsers
    sub_parsers = parser.add_subparsers(help='sub-command help')

    # ping
    parser_ping = sub_parsers.add_parser('ping', help='proof of life - returns text reversed')
    parser_ping.add_argument('--text', type=str, help='text to reverse')
    parser_ping.set_defaults(func=ping)


    # chat/prompt
    parser_chat_prompt = sub_parsers.add_parser('chat', help='chat with LLM')
    parser_chat_prompt.add_argument('--prompt', type=str, help='text to prompt LLM')
    parser_chat_prompt.add_argument('--repo',  type=str, help='repository owner/repo/branch')
    parser_chat_prompt.add_argument('--context',  type=str, help='filenames, array')
    parser_chat_prompt.set_defaults(func=chat_prompt)

    # repo/list
    parser_repo_list = sub_parsers.add_parser('repo-list', help='list repositories for RAG')
    parser_repo_list.set_defaults(func=repo_list)

    # repo/vectorize
    parser_repo_vectorize = sub_parsers.add_parser('repo-vectorize', help='vectorize repository')
    parser_repo_vectorize.add_argument('--repo', type=str, help='repository owner/repo/branch')
    parser_repo_vectorize.set_defaults(func=repo_vectorize)

    # repo/delete
    parser_repo_delete = sub_parsers.add_parser('repo-delete', help='delete repository')
    parser_repo_delete.add_argument('--repo', type=str, help='repository owner/repo/branch')
    parser_repo_delete.set_defaults(func=repo_delete)



    args = parser.parse_args()
    args.func(args)



