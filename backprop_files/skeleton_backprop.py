#!/usr/bin/env python3
import numpy as np
from io import StringIO

NUM_FEATURES = 124 #features are 1 through 123 (123 only in test set), +1 for the bias
DATA_PATH = "./data/adult/" #TODO: if doing development somewhere other than the cycle server, change this to the directory where a7a.train, a7a.dev, and a7a.test are

#returns the label and feature value vector for one datapoint (represented as a line (string) from the data file)
def parse_line(line):
    tokens = line.split()
    x = np.zeros(NUM_FEATURES)
    y = int(tokens[0])
    y = max(y,0) #treat -1 as 0 instead, because sigmoid's range is 0-1
    for t in tokens[1:]:
        parts = t.split(':')
        feature = int(parts[0])
        value = int(parts[1])
        x[feature-1] = value
    x[-1] = 1 #bias
    return y, x

#return labels and feature vectors for all datapoints in the given file
def parse_data(filename):
    with open(filename, 'r') as f:
        vals = [parse_line(line) for line in f]
        (ys, xs) = ([v[0] for v in vals],[v[1] for v in vals])
        return np.asarray([ys],dtype=np.float32).T, np.asarray(xs,dtype=np.float32).reshape(len(xs),NUM_FEATURES,1) #returns a tuple, first is an array of labels, second is an array of feature vectors

def init_model(args):
    w1 = None
    w2 = None

    if args.weights_files:
        with open(args.weights_files[0], 'r') as f1:
            w1 = np.loadtxt(f1)
        with open(args.weights_files[1], 'r') as f2:
            w2 = np.loadtxt(f2)
            w2 = w2.reshape(1,len(w2))
    else:
        #TODO (optional): If you want, you can experiment with a different random initialization. As-is, each weight is uniformly sampled from [-0.5,0.5).
        w1 = np.random.rand(args.hidden_dim, NUM_FEATURES) #bias included in NUM_FEATURES
        w2 = np.random.rand(1, args.hidden_dim + 1) #add bias column

    #At this point, w1 has shape (hidden_dim, NUM_FEATURES) and w2 has shape (1, hidden_dim + 1). In both, the last column is the bias weights.


    #TODO: Replace this with whatever you want to use to represent the network; you could use use a tuple of (w1,w2), make a class, etc.
    model = None
    class Model():
        def __init__(self):
            self.l1_in_w1 = w1
            self.l1_out_w2 = w2
            self.l1_in_z = np.zeros([w1.shape[0], 1])
            self.l1_out_a = np.zeros([w1.shape[0]+1, 1])
            self.l1_out_a[-1, :] = 1
            self.l2_in_z = 0
            self.l2_out_y = 0

        def sigmoid(self, x):
            s = 1/(1+np.exp(-x))
            return s

        def sigmoid_derivation(self, x):
            s = 1/(1+np.exp(-x))
            ds = s*(1-s)
            return ds

        def forward(self, xs):
            self.l1_in_z = np.dot(self.l1_in_w1, xs)
            self.l1_out_a[:-1, :] = self.sigmoid(self.l1_in_z)
            self.l2_in_z = np.dot(self.l1_out_w2, self.l1_out_a)
            self.l2_out_y = self.sigmoid(self.l2_in_z)

        def backprop(self, ys, xs):
            l2_da = self.sigmoid_derivation(self.l2_in_z)
            l1_out_w2 = self.l1_out_w2
            self.l1_out_w2 = self.l1_out_w2 - args.lr*(self.l2_out_y - ys)*l2_da*self.l1_out_a.T
            l1_da = self.sigmoid_derivation(self.l1_in_z)
            self.l1_in_w1 = self.l1_in_w1 - args.lr*(self.l2_out_y - ys)*l2_da*np.dot(np.multiply(l1_da, l1_out_w2[:,:-1].T), xs.T)

    model = Model()
    # raise NotImplementedError #TODO: delete this once you implement this function
    return model

def train_model(model, train_ys, train_xs, dev_ys, dev_xs, args):
    #TODO: Implement training for the given model, respecting args
    dev_accuracy = 0.0
    flag = 0
    dev_w1 = model.l1_in_w1
    dev_w2 = model.l1_out_w2
    while args.iterations:
        for i in range(train_ys.shape[0]):
            model.forward(train_xs[i])
            model.backprop(train_ys[i], train_xs[i, :, :])
        args.iterations -= 1
        if not args.nodev:
            accuracy = test_accuracy(model, dev_ys, dev_xs)
            if args.devmode == 0:
                if accuracy<dev_accuracy:
                    break
                else:
                    dev_accuracy = accuracy
            elif args.devmode == 1:
                if flag == 10 or args.iterations == 0:
                    model.l1_in_w1 = dev_w1
                    model.l1_out_w2 = dev_w2
                    break
                elif accuracy>=dev_accuracy and flag < 10:
                    flag = 0
                    dev_accuracy = accuracy
                    dev_w1 = model.l1_in_w1
                    dev_w2 = model.l1_out_w2
                else:
                    flag += 1

    # raise NotImplementedError #TODO: delete this once you implement this function
    return model


def plot_result(model, train_ys, train_xs, dev_ys, dev_xs, test_ys, test_xs, args):
    import matplotlib.pyplot as plt

    iterations = 50
    lr = [1.0, 0.25, 0.02]
    hidden_dim = [5, 15, 25]
    dev_acc = np.zeros([3, 3, 50])
    test_acc = np.zeros([3, 3, 50])
    args.iterations = iterations
    for i in range(0, len(lr)):
        for j in range(0, len(hidden_dim)):
            args.hidden_dim = hidden_dim[j]
            args.lr = lr[i]
            model = init_model(args)
            for t in range(0, args.iterations):
                for p in range(train_ys.shape[0]):
                    model.forward(train_xs[p])
                    model.backprop(train_ys[p], train_xs[p, :, :])
                dev_acc[i, j, t] = test_accuracy(model, dev_ys, dev_xs)
                test_acc[i, j, t] = test_accuracy(model, test_ys, test_xs)
                print(t)
    ite = list(range(iterations))
    plt.subplot(1, 3, 1)
    plt.plot(ite, dev_acc[0, 0, :])
    plt.plot(ite, test_acc[0, 0, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 1, hidden_dim = 5')
    plt.legend(['dev_acc', 'test_acc'])
    plt.subplot(1, 3, 2)
    plt.plot(ite, dev_acc[0, 1, :])
    plt.plot(ite, test_acc[0, 1, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 1, hidden_dim = 15')
    plt.legend(['dev_acc', 'test_acc'])
    plt.subplot(1, 3, 3)
    plt.plot(ite, dev_acc[0, 2, :])
    plt.plot(ite, test_acc[0, 2, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 1, hidden_dim = 25')
    plt.legend(['dev_acc', 'test_acc'])
    plt.show()

    plt.subplot(2, 3, 1)
    plt.plot(ite, dev_acc[1, 0, :])
    plt.plot(ite, test_acc[1, 0, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 0.25, hidden_dim = 5')
    plt.legend(['dev_acc', 'test_acc'])
    plt.subplot(2, 3, 2)
    plt.plot(ite, dev_acc[1, 1, :])
    plt.plot(ite, test_acc[1, 1, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 0.25, hidden_dim = 15')
    plt.legend(['dev_acc', 'test_acc'])
    plt.subplot(2, 3, 3)
    plt.plot(ite, dev_acc[1, 2, :])
    plt.plot(ite, test_acc[1, 2, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 0.25, hidden_dim = 25')
    plt.legend(['dev_acc', 'test_acc'])
    plt.show()

    plt.subplot(3, 3, 1)
    plt.plot(ite, dev_acc[2, 0, :])
    plt.plot(ite, test_acc[2, 0, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 0.02, hidden_dim = 5')
    plt.legend(['dev_acc', 'test_acc'])
    plt.subplot(3, 3, 2)
    plt.plot(ite, dev_acc[2, 1, :])
    plt.plot(ite, test_acc[2, 1, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 0.02, hidden_dim = 15')
    plt.legend(['dev_acc', 'test_acc'])
    plt.subplot(3, 3, 3)
    plt.plot(ite, dev_acc[2, 2, :])
    plt.plot(ite, test_acc[2, 2, :])
    plt.xlabel('iterations')
    plt.ylabel('accuracy')
    plt.title('lr = 0.02, hidden_dim = 25')
    plt.legend(['dev_acc', 'test_acc'])
    plt.show()

def test_accuracy(model, test_ys, test_xs):
    accuracy = 0.0
    #TODO: Implement accuracy computation of given model on the test data
    c = 0
    for i in range(test_ys.shape[0]):
        model.forward(test_xs[i, :, :])
        if model.l2_out_y >= 0.5:
            y = 1
        else:
            y = 0
        y = np.sign(y)
        if y == test_ys[i]:
            c += 1
    accuracy = c/test_ys.shape[0]
    #raise NotImplementedError #TODO: delete this once you implement this function
    return accuracy

def extract_weights(model):
    w1 = None
    w2 = None
    #TODO: Extract the two weight matrices from the model and return them (they should be the same type and shape as they were in init_model, but now they have been updated during training)
    w1 = model.l1_in_w1
    w2 = model.l1_out_w2
    #raise NotImplementedError #TODO: delete this once you implement this function
    return w1, w2

def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Neural network with one hidden layer, trainable with backpropagation.')
    parser.add_argument('--nodev', action='store_true', default=False, help='If provided, no dev data will be used.')
    parser.add_argument('--iterations', type=int, default=20, help='Number of iterations through the full training data to perform.')
    parser.add_argument('--lr', type=float, default=0.1, help='Learning rate to use for update in training loop.')

    weights_group = parser.add_mutually_exclusive_group()
    weights_group.add_argument('--weights_files', nargs=2, metavar=('W1','W2'), type=str, help='Files to read weights from (in format produced by numpy.savetxt). First is weights from input to hidden layer, second is from hidden to output.')
    weights_group.add_argument('--hidden_dim', type=int, default=5, help='Dimension of hidden layer.')

    parser.add_argument('--print_weights', action='store_true', default=False, help='If provided, print final learned weights to stdout (used in autograding)')

    parser.add_argument('--train_file', type=str, default=os.path.join(DATA_PATH,'a7a.train'), help='Training data file.')
    parser.add_argument('--dev_file', type=str, default=os.path.join(DATA_PATH,'a7a.dev'), help='Dev data file.')
    parser.add_argument('--test_file', type=str, default=os.path.join(DATA_PATH,'a7a.test'), help='Test data file.')
    parser.add_argument('--plot', action='store_true', default=False,
                        help='if provided, plot analysis will be processed')
    parser.add_argument('--devmode', type=int, default=0,
                        help='choose the mode of the using of dev data, --devmode 0 means simple use, when accuracy decrese then stop, --devmode 1 means no more five next iteration increase the accuracy, then stop.')

    args = parser.parse_args()

    """
    At this point, args has the following fields:

    args.nodev: boolean; if True, you should not use dev data; if False, you can (and should) use dev data.
    args.iterations: int; number of iterations through the training data.
    args.lr: float; learning rate to use for training update.
    args.weights_files: iterable of str; if present, contains two fields, the first is the file to read the first layer's weights from, second is for the second weight matrix.
    args.hidden_dim: int; number of hidden layer units. If weights_files is provided, this argument should be ignored.
    args.train_file: str; file to load training data from.
    args.dev_file: str; file to load dev data from.
    args.test_file: str; file to load test data from.
    """
    train_ys, train_xs = parse_data(args.train_file)
    dev_ys = None
    dev_xs = None
    if not args.nodev:
        dev_ys, dev_xs= parse_data(args.dev_file)
    test_ys, test_xs = parse_data(args.test_file)

    model = init_model(args)
    model = train_model(model, train_ys, train_xs, dev_ys, dev_xs, args)
    accuracy = test_accuracy(model, test_ys, test_xs)
    print('Test accuracy: {}'.format(accuracy))
    if args.print_weights:
        w1, w2 = extract_weights(model)
        with StringIO() as weights_string_1:
            np.savetxt(weights_string_1,w1)
            print('Hidden layer weights: {}'.format(weights_string_1.getvalue()))
        with StringIO() as weights_string_2:
            np.savetxt(weights_string_2,w2)
            print('Output layer weights: {}'.format(weights_string_2.getvalue()))
    if args.plot:
        plot_result(model, train_ys, train_xs, dev_ys, dev_xs, test_ys, test_xs, args)


if __name__ == '__main__':
    main()
