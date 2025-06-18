import PyInstaller.__main__

PyInstaller.__main__.run([
    'work_plan_app.py',  # 你的Python文件名
    '--onefile',         # 打包为单个文件
    '--windowed',        # 不显示控制台窗口
    '--icon=app.ico',    # 可选：添加图标文件
    '--name=WorkPlanTool'  # 可执行文件名称
])
    # '--onefile',         # 打包为单个文件
    # '--windowed',        # 不显示控制台窗口