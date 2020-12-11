import os

def get_size(filename: str) -> str:
    """将os.path.getsize()得到的字节数，转化为易读的表示\n
    例如：输出'2 KB'

    Args:
        filename (str): 文件路径

    Returns:
        str: 文件大小
    """
    size = os.path.getsize(filename)
    if pow(2,10)<size<=pow(2,20):
        return f'{size/pow(2,10):.2f} KB'
    elif pow(2,20)<size<=pow(2,30):
        return f'{size/pow(2,20):.2f} MB'
    elif pow(2,30)<size<=pow(2,40):
        return f'{size/pow(2,30):.2f} GB'
    else:
        return f'{size} B'

