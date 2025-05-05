我使用的是windows环境。

前端部署：
cd fronted
npm install(可选，第一次启动需要安装依赖)
npm start

后端部署：
cd backend
.\venv\Scripts\activate 进入虚拟环境
pip install -r requirements.txt (可选，第一次启动需要安装依赖)
python.exe app.py

大模型：
下载ollama (第一次启动需要安装依赖)
ollama run deepseek-r1

