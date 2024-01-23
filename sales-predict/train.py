import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import torch
from torch import nn
from torch.autograd import Variable
from scipy import stats
from torch.utils.data import DataLoader

hidden_size = 1024
cuda_switch = torch.cuda.is_available()
look_back = 60
predict_days = 14
train_times = 1000
learning_rate = 0.00005 # 0.001 lr
batch_size = 10240

target_name = 'pred'

df = pd.read_csv("data/sales.max.csv")
df.index = pd.to_datetime(df['date'])
df = df.sort_index(ascending=False)
df = df[['month', 'day', 'weekday', 'sales']]
df = df.dropna()
df = df.groupby(['date'])['sales'].sum().reset_index()
df['date'] = pd.to_datetime(df['date'])
df['day'] = df['date'].dt.day
df['month'] = df['date'].dt.month
df['weekday'] = df['date'].dt.weekday
df['pred'] = df['sales'].shift(-predict_days)
df = df[['month', 'day', 'weekday', 'sales', 'pred']]

input_dim = len(df.columns) - 1

df.dropna(inplace=True)

X, y = df.drop(columns=[target_name]), df[target_name].values
X.shape, y.shape

mm = MinMaxScaler()
# mm = StandardScaler()
ss = StandardScaler()

X_trans = ss.fit_transform(X)
y_trans = mm.fit_transform(y.reshape(-1, 1))

def split_sequences(input_sequences, output_sequence, n_steps_in, n_steps_out):
    X, y = list(), list() # instantiate X and y
    for i in range(len(input_sequences)):
        # find the end of the input, output sequence
        end_ix = i + n_steps_in
        out_end_ix = end_ix + n_steps_out - 1
        # check if we are beyond the dataset
        if out_end_ix > len(input_sequences): break
        # gather input and output of the pattern
        seq_x, seq_y = input_sequences[i:end_ix], output_sequence[end_ix-1:out_end_ix, -1]
        X.append(seq_x), y.append(seq_y)
    return np.array(X), np.array(y)

X_ss, y_mm = split_sequences(X_trans, y_trans, look_back, predict_days)
print(X_ss.shape, y_mm.shape)

total_samples = len(X)
train_test_cutoff = round(0.80 * total_samples)

X_train = X_ss[:train_test_cutoff]
X_test = X_ss[train_test_cutoff:]

y_train = y_mm[:train_test_cutoff]
y_test = y_mm[train_test_cutoff:] 

print("Training Shape:", X_train.shape, y_train.shape)
print("Testing Shape:", X_test.shape, y_test.shape) 

X_train_tensors = Variable(torch.Tensor(X_train))
X_test_tensors = Variable(torch.Tensor(X_test))

y_train_tensors = Variable(torch.Tensor(y_train))
y_test_tensors = Variable(torch.Tensor(y_test))

X_train_tensors_final = torch.reshape(X_train_tensors,   
                                      (X_train_tensors.shape[0], look_back, 
                                       X_train_tensors.shape[2]))
X_test_tensors_final = torch.reshape(X_test_tensors,
                                     (X_test_tensors.shape[0], look_back, 
                                      X_test_tensors.shape[2]))
# X_train_tensors_final = DataLoader(X_train_tensors_final, batch_size=batch_size, shuffle=False)
# y_train_tensors = DataLoader(y_train_tensors, batch_size=batch_size, shuffle=False)

# print("Training Shape:", X_train_tensors_final.shape, y_train_tensors.shape)
# print("Testing Shape:", X_test_tensors_final.shape, y_test_tensors.shape) 

class LSTM(nn.Module):
    
    def __init__(self, num_classes, input_size, hidden_size, num_layers):
        super().__init__()
        self.num_classes = num_classes # output size
        self.num_layers = num_layers # number of recurrent layers in the lstm
        self.input_size = input_size # input size
        self.hidden_size = hidden_size # neurons in each lstm layer
        # LSTM model
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True) # lstm
        self.fc_1 =  nn.Linear(hidden_size, 128) # fully connected 
        self.fc_2 = nn.Linear(128, num_classes) # fully connected last layer
        self.relu = nn.ReLU()
        
    def forward(self,x):
        # hidden state
        h_0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size)).cuda()
        # cell state
        c_0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size)).cuda()
        # propagate input through LSTM
        output, (hn, cn) = self.lstm(x, (h_0, c_0)) # (input, hidden, and internal state)
        hn = hn.view(-1, self.hidden_size) # reshaping the data for Dense layer next
        out = self.relu(hn)
        out = self.fc_1(out) # first dense
        out = self.relu(out) # relu
        out = self.fc_2(out) # final output
        return out
    
def training_loop(n_epochs, lstm, optimiser, loss_fn, X_train, y_train,
                  X_test, y_test):
  for epoch in range(n_epochs):
    # for i, data in enumerate(zip(X_train, y_train)):
    #   x_t = data[0].cuda()
    #   y_t = data[1].cuda()
      lstm.train()
      outputs = lstm.forward(X_train.cuda()) # forward pass
      optimiser.zero_grad() # calculate the gradient, manually setting to 0
      # obtain the loss function
      loss = loss_fn(outputs, y_train.cuda())
      loss.backward() # calculates the loss of the loss function
      optimiser.step() # improve from loss, i.e backprop
      # test loss
      lstm.eval()
      test_preds = lstm(X_test.cuda())
      test_loss = loss_fn(test_preds, y_test.cuda())
      print(f"Epoch: {epoch}, train loss: {loss.item()}, test loss: {test_loss.item()}")

input_size = input_dim # number of features
num_layers = 1 # number of stacked lstm layers

num_classes = predict_days # number of output classes 

lstm = LSTM(num_classes, 
              input_size, 
              hidden_size, 
              num_layers).to('cuda')

loss_fn = torch.nn.MSELoss()    # mean-squared error for regression
optimiser = torch.optim.Adam(lstm.parameters(), lr=learning_rate)

training_loop(n_epochs=train_times,
              lstm=lstm,
              optimiser=optimiser,
              loss_fn=loss_fn,
              X_train=X_train_tensors_final,
              y_train=y_train_tensors,
              X_test=X_test_tensors_final,
              y_test=y_test_tensors)

df_X_ss = ss.transform(df.drop(columns=['pred'])) # old transformers
df_y_mm = mm.transform(df.pred.values.reshape(-1, 1)) # old transformers
# split the sequence
df_X_ss, df_y_mm = split_sequences(df_X_ss, df_y_mm, look_back, predict_days)
# converting to tensors
df_X_ss = Variable(torch.Tensor(df_X_ss))
df_y_mm = Variable(torch.Tensor(df_y_mm))
# reshaping the dataset
df_X_ss = torch.reshape(df_X_ss, (df_X_ss.shape[0], look_back, df_X_ss.shape[2]))

train_predict = lstm(df_X_ss.cuda()) # forward pass
data_predict = train_predict.data.cpu().numpy() # numpy conversion
dataY_plot = df_y_mm.data.numpy()

data_predict = mm.inverse_transform(data_predict) # reverse transformation
dataY_plot = mm.inverse_transform(dataY_plot)
true, preds = [], []
for i in range(train_test_cutoff, len(dataY_plot)):
    true.append(dataY_plot[i][0])
for i in range(train_test_cutoff, len(data_predict)):
    preds.append(data_predict[i][0])
plt.figure(figsize=(10,6)) #plotting
# plt.axvline(x=train_test_cutoff, c='r', linestyle='--') # size of the training set

plt.plot(true, label='Actual Data') # actual plot
plt.plot(preds, label='Predicted Data') # predicted plot
plt.title('Time-Series Prediction')
plt.legend()
plt.savefig("whole_plot.png", dpi=300)
plt.show() 