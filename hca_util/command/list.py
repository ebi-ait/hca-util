from hca_util.common import format_err
from hca_util.local_state import get_selected_area


class CmdList:
    """
    user: both wrangler and contributor
    aws resource or client used in command - s3 resource (bucket.objects, Object().metadata)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        if self.args.b:  # list all areas in bucket
            if self.aws.is_contributor:
                return False, 'You don\'t have permission to use this command'
            try:
                folder_count = 0
                for area in self.list_bucket_areas():
                    k = area["key"]
                    print(k, end=' ')
                    p = ''
                    if 'perms' in area:
                        p = area.get('perms') or ''
                    print(p.ljust(3), end=' ')
                    if 'name' in area:
                        n = area.get('name')
                        print(f'{n}' if n else '', end=' ')
                    print()
                    folder_count += 1
                print_count(folder_count)
                return True, None

            except Exception as e:
                return False, format_err(e, 'list')

        else:  # list selected area contents
            selected_area = get_selected_area()

            if not selected_area:
                return False, 'No area selected'

            try:
                selected_area += '' if selected_area.endswith('/') else '/'

                file_count = 0
                for k in self.list_area_contents(selected_area):
                    print(k)
                    if not k.endswith('/'):
                        file_count += 1

                print_count(file_count)
                return True, None
            except Exception as e:
                return False, format_err(e, 'list')

    def list_bucket_areas(self):
        areas = []
        s3_resource = self.aws.common_session.resource('s3')
        bucket = s3_resource.Bucket(self.aws.bucket_name)
        for obj in bucket.objects.all():
            k = obj.key
            if k.endswith('/'):
                obj_meta = obj.Object().metadata
                if obj_meta:
                    areas.append(dict(
                        key=k, perms=obj_meta.get('perms'), name=obj_meta.get('name')
                    ))
                else:
                    areas.append(dict(
                        key=k, perms=None, name=None
                    ))
        return areas

    def list_area_contents(self, selected_area):
        contents = []

        s3_resource = self.aws.common_session.resource('s3')
        bucket = s3_resource.Bucket(self.aws.bucket_name)

        for obj in bucket.objects.filter(Prefix=selected_area):
            k = obj.key
            contents.append(k)

        return contents


def print_count(count):
    if count == 0:
        print('No item')
    elif count == 1:
        print('1 item')
    else:
        print(f'{count} items')
