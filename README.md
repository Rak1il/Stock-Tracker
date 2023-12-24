## Overview
The stock market is an ever-changing (dynamic) environment whose movements and fluctuations are affected by many factors such as news, previous prices and several other factors. As news and previous prices are considered one of the most important factors influencing the market and we want to measure the extent of the news’s impact on prices, predict the next price based on previous prices using deep learning techniques to help market analysts detect fraud or insider trading.
## Table of Contents
- [Requirements](#Requirements)
- [Installation](#installation)
- [Usage](#Usage)
- [Data](#Data)
- [Models](#Models)
- [Results](#Results)
- [Contributing](#Contributing)
- [License](#License)
## Requirements
- Python 3.9 or higher
## Installation
```bash
#pip install ta
#pip install TA-Lib
```
## Usage
To use the stock tracker project, follow these steps:
1. Prepare the data: Ensure that you have historical stock price data in a compatible format. You may need to preprocess the data or convert it into a specific format before training the models.
2. Train the models: Run the training script to train the LSTM and GRU models on your historical stock price data. Adjust the hyperparameters and model architecture as needed.
3. Make predictions: Use the trained models to make predictions on new or unseen data. This can be done by running the prediction script and providing the necessary inputs.
4. Evaluate the models: Assess the performance of the models by comparing the predicted closing prices with the actual prices. Calculate evaluation metrics : mean absolute error (MAE).

## Data

The stock tracker project requires historical stock price data to train and evaluate the models. Ensure that the data is in a suitable format, such as a CSV file, with columns representing the date, open price, high price, low price, closing price, and volume.

You may find relevant stock price datasets from various sources, such as financial APIs or publicly available datasets. Ensure that you have the necessary permissions or licenses to use the data for your project.

## Models

The stock tracker project employs LSTM and GRU models for predicting stock closing prices. These models are well-suited for capturing temporal dependencies and patterns in sequential data.

The LSTM model consists of LSTM layers followed by one or more fully connected layers. The GRU model follows a similar architecture, but utilizes Gated Recurrent Units instead of LSTM units.

The models can be customized by adjusting various hyperparameters, such as the number of hidden units, the number of layers, the learning rate, and the activation functions. Experiment with different configurations to achieve the best performance.

## Results

After training and evaluating the models, you can analyze the results to determine their accuracy and reliability. Plot the predicted closing prices against the actual prices to visually assess the performance of the models.

Additionally, calculate evaluation metrics such as mean squared error (MSE), root mean squared error (RMSE), mean absolute error (MAE), or other appropriate metrics to quantitatively evaluate the models' performance.

## Contributing
Contributions to the stock tracker project are welcome! If you have any ideas, suggestions, or improvements, feel free to open an issue or submit a pull request. Please follow the existing code style and guidelines.
