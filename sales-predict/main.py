import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from torch.utils.data import DataLoader, TensorDataset

# df = pd.read_csv('data/sales.csv')
# df['date'] = pd.to_datetime(df['date'])
# df['month'] = df['date'].dt.month
# df['day'] = df['date'].dt.day
# df['weekday'] = df['date'].dt.weekday
# df = df[['date', 'month', 'day', 'weekday', 'sales', 'product_id', 'store_id']]
# df.to_csv('data/sales.clean.csv', index=False)

# df = pd.read_csv('data/sales.clean.csv')
# groups = df.groupby(['product_id'])
# # find the group with the most sales
# max_group = max(groups, key=lambda x: x[1]['sales'].sum())
# print(max_group)
# max_group[1].to_csv('data/sales.max.csv', index=False)
df = pd.read_csv('data/sales.max.csv')
df = df[['date', 'month', 'day', 'weekday', 'sales']]
df = df.dropna()
df = df.groupby(['date'])['sales'].sum().reset_index()
df['date'] = pd.to_datetime(df['date'])
df['day'] = df['date'].dt.day
df['month'] = df['date'].dt.month
df['weekday'] = df['date'].dt.weekday

print(df)

# 准备数据集
sequence_length = 15  # 滑动时间窗口大小
data = df[['sales', 'day', 'month', 'weekday']].values.astype(float)
data_sequence = []

# 创建滑动窗口数据
for i in range(len(data) - sequence_length):
  data_sequence.append(data[i:i + sequence_length])

# 将数据转换为 PyTorch 张量
data_sequence = np.array(data_sequence)
data_sequence = torch.from_numpy(data_sequence).float()

# 准备训练集和测试集
train_size = int(len(data) * 0.8)
test_size = len(data) - train_size
train_data, test_data = data[:train_size], data[train_size:]

# 创建 DataLoader 对象
train_loader = DataLoader(train_data, batch_size=64, shuffle=False)
test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

# 定义 LSTM 模型
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

# 初始化模型、损失函数和优化器
input_size = data_sequence.shape[2]  # 输入特征的维度（单变量）
print(input_size)
hidden_size = 64  # LSTM 隐藏层单元数
output_size = 1  # 输出维度（单变量预测）
model = LSTMModel(input_size, hidden_size, output_size)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 训练模型
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    for inputs in train_loader:
        optimizer.zero_grad()
        inputs = inputs.view(-1, sequence_length, input_size)
        outputs = model(inputs)
        loss = criterion(outputs.squeeze(), inputs[:, -1, :])  # 预测销售数据
        loss.backward()
        optimizer.step()

    # 在测试集上进行评估
    model.eval()
    with torch.no_grad():
        total_loss = 0
        for inputs in test_loader:
            inputs = inputs.view(-1, sequence_length, input_size)
            outputs = model(inputs)
            loss = criterion(outputs.squeeze(), inputs[:, -1, :])
            total_loss += loss.item() * len(inputs)
        
        avg_loss = total_loss / len(test_loader.dataset)
        print(f"Epoch {epoch+1}, Test Loss: {avg_loss}")