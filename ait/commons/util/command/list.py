from ait.commons.util.common import format_err, is_valid_area_name
from ait.commons.util.local_state import get_selected_area


class CmdList:
    """
    admin and user
    aws resource or client used in command - s3 resource (list_objects_v2, get_object_tagging)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args
        
        self.s3_cli = self.aws.common_session.client('s3')

    def run(self):

        if self.args.b:  # list all areas in bucket
            if self.aws.is_user:
                return False, 'You don\'t have permission to use this command'
            
            try:
                folder_count = 0
                for area in self.list_bucket_areas():
                    k = area["key"]
                    self.print_area(k, area)
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
                n, p = self.get_name_and_perms(selected_area)
                self.print_area(selected_area, dict(name=n, perms=p))

                file_count = 0
                for k in self.list_area_contents(selected_area):
                    print(k)
                    if not k.endswith('/'):
                        file_count += 1

                print_count(file_count)
                return True, None
            except Exception as e:
                return False, format_err(e, 'list')

    def print_area(self, k, area):
        print(k, end=' ')
        p = ''
        if 'perms' in area:
            p = area.get('perms') or ''
        print(p.ljust(3), end=' ')
        if 'name' in area:
            n = area.get('name')
            print(f'{n}' if n else '', end=' ')
        print()
    
    def get_name_and_perms(self, k):
        n, p = None, None
        try: 
            tagSet = self.s3_cli.get_object_tagging(Bucket=self.aws.bucket_name, Key=k)

            if tagSet and tagSet['TagSet']:
                kv = dict((tag['Key'], tag['Value']) for tag in tagSet['TagSet'])
                n = kv.get('name', None)
                p = kv.get('perms', None)
            else: # for backward compatibility get name and perms from metadata
                if not self.aws.is_user: # only admin can retrieve metadata (head_object)
                    resp = self.s3_cli.head_object(Bucket=self.aws.bucket_name, Key=k)
                    if resp and resp['Metadata']:
                        meta = resp['Metadata']
                        n = meta.get('name', None)
                        p = meta.get('perms', None)
        except:
            pass 
        return n, p

    def list_bucket_areas(self):
        areas = []
        result = self.s3_cli.list_objects_v2(Bucket=self.aws.bucket_name, Delimiter='/')
        dirs = result.get('CommonPrefixes', [])
        for d in dirs:
            k = d.get('Prefix')
            if is_valid_area_name(k):
                n, p = self.get_name_and_perms(k)
                areas.append(dict(key=k, name=n, perms=p))
        return areas

    def list_area_contents(self, selected_area):
        contents = []

        s3_resource = self.aws.common_session.resource('s3')
        bucket = s3_resource.Bucket(self.aws.bucket_name)

        for obj in bucket.objects.filter(Prefix=selected_area):
            k = obj.key
            if k != selected_area:
                contents.append(k)

        return contents


def print_count(count):
    if count == 0:
        print('No item')
    elif count == 1:
        print('1 item')
    else:
        print(f'{count} items')
