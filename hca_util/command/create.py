from .command import HcaCmd


class CmdCreate(HcaCmd):

    def cmd_create(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) > 2:
            print('Invalid args. See `help create`')
            return

        # generate random uuid prefix for directory name
        dir_name = gen_uuid()

        # valid input
        # 1. create
        # 2. create [-udx]
        # 3. create [project_name]
        # 4. create [project_name] [-udx]

        def verify_perms(permissions):
            is_valid_perms = permissions in allowed_perms_combinations
            if not is_valid_perms:
                permissions = default_perms
                print('Invalid perms, using default')
            print(f'Perms <{permissions}>')
            return permissions

        def verify_projname(proj_name):
            is_valid_projname = is_valid_project_name(proj_name)
            if not is_valid_projname:
                proj_name = ''
                print('Invalid project name, ignoring')
            print(f'Project name <{proj_name}>')
            return proj_name

        project_name = ''
        perms = default_perms
        if len(argv) == 0:
            print(f'Project name <>')
            print(f'Default perms <{perms}>')
        elif len(argv) == 1 and argv[0].startswith('-'):
            print(f'Project name <>')
            perms = verify_perms(argv[0][1:])
        elif len(argv) == 1 and not argv[0].startswith('-'):
            project_name = verify_projname(argv[0])
            print(f'Default perms <{perms}>')
        elif len(argv) == 2 and argv[1].startswith('-'):
            project_name = verify_projname(argv[0])
            perms = verify_perms(argv[1][1:])
        else:
            print('Invalid args. See `help create`')
            return

        try:

            self.aws.s3.put_object(Bucket=self.bucket_name, Key=(dir_name + '/'), Metadata={'name': f'{project_name}'})
            print('Created ' + dir_name)

            # get bucket policy
            s3_resource = self.session.resource('s3')
            try:
                bucket_policy = s3_resource.BucketPolicy(self.bucket_name)
                policy_str = bucket_policy.policy
            except ClientError:
                policy_str = ''

            if policy_str:
                policy_json = json.loads(policy_str)
            else:  # no bucket policy
                policy_json = json.loads('{ "Version": "2012-10-17", "Statement": [] }')

            # add new statement for dir to existing bucket policy
            new_statement = new_policy_statement(self.bucket_name, dir_name, perms)
            policy_json['Statement'].append(new_statement)

            updated_policy = json.dumps(policy_json)

            bucket_policy.put(Policy=updated_policy)

        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in cmd create.\nDetail: ' + str(e))
