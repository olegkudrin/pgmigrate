import os
import subprocess
import sys

import yaml

from behave import given, then, when


def run_pgmigrate(migr_dir, args):
    cmd = ['coverage', 'run', '-p', '--include=pgmigrate.py',
           './pgmigrate.py', '-vvv', '-d', migr_dir,
           '-c', 'dbname=pgmigratetest'] + str(args).split(' ')

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    stdout, stderr = p.communicate()
    return p.returncode, str(stdout), str(stderr)

@given('successful pgmigrate run with "{args}"')
def step_impl(context, args):
    if context.migrate_config:
        with open(os.path.join(context.migr_dir, 'migrations.yml'), 'w') as f:
            f.write(yaml.dump(context.migrate_config))
    res = run_pgmigrate(context.migr_dir, args)

    if res[0] != 0:
        sys.stdout.write(res[1])
        sys.stderr.write(res[2])
        raise Exception('Expected success got retcode=%d' % res[0])


@when('we run pgmigrate with "{args}"')  # noqa
def step_impl(context, args):
    if context.migrate_config:
        with open(os.path.join(context.migr_dir, 'migrations.yml'), 'w') as f:
            f.write(yaml.dump(context.migrate_config))
    res = run_pgmigrate(context.migr_dir, args)

    context.last_migrate_res = {'ret': res[0], 'out': res[1], 'err': res[2]}


@then('pgmigrate command "{result}"')  # noqa
def step_impl(context, result):
    if not context.last_migrate_res:
        raise Exception('No pgmigrate run detected in current context')

    if result == 'failed' and context.last_migrate_res['ret'] == 0:
        sys.stdout.write(str(context.last_migrate_res['out']))
        sys.stderr.write(str(context.last_migrate_res['err']))
        raise Exception('Expected failure got success')
    elif result == 'succeeded' and context.last_migrate_res['ret'] != 0:
        sys.stdout.write(str(context.last_migrate_res['out']))
        sys.stderr.write(str(context.last_migrate_res['err']))
        raise Exception('Expected success got retcode='
                        '%d' % context.last_migrate_res['ret'])
    elif result not in ['failed', 'succeeded']:
        raise Exception('Incorrect step arguments')
