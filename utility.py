def read_list_from_file(filename):
    result = []
    # open file and read the content in a list
    with open(filename, 'r') as file_handle:
        for line in file_handle:
            # remove linebreak which is the last character of the string
            item = line[:-1]

            # add item to the list
            result.append(item)
    return result


def write_list_to_file(filename, list_to_write):
    with open(filename, 'w') as file_handle:
        for item in list_to_write:
            file_handle.write('%s\n' % item)
    return


def append_list_to_file(filename, list_to_append):
    full_list = read_list_from_file(filename)
    full_list.extend(list_to_append)
    write_list_to_file(filename, full_list)


def append_item_to_file(filename, item):
    full_list = read_list_from_file(filename)
    full_list.append(item)
    write_list_to_file(filename, full_list)
