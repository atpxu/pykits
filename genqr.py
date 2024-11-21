import qrcode

def generate_qr_code(data: str, filename: str):
    """
    生成二维码并保存到指定文件名
    :param data: 要编码的字符串
    :param filename: 保存二维码的文件名（支持 .png, .jpg 等）
    """
    # 创建二维码对象
    qr = qrcode.QRCode(
        version=1,  # 控制二维码大小，1 是最小的
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 容错率
        box_size=10,  # 每个点的大小
        border=4,  # 边框厚度
    )
    # 添加数据
    qr.add_data(data)
    qr.make(fit=True)
    # 生成图像
    img = qr.make_image(fill_color="black", back_color="white")
    # 保存到指定文件
    img.save(filename)
    print(f"二维码已保存到 {filename}")

# 示例用法
if __name__ == "__main__":
    generate_qr_code("https://www.example.com", "example_qr.png")
