import numpy as np
import cpickle as pickle 
import gym

h = 200
batch_size = 10
learning_rate = 1e-4
gamma = 0.99 # discount factor
decay_rate = 0.99
resume = False

#init model 
D = 80*80 
if resume:
	model = pickle.load(open('save.p', 'rb'))
else:
	mocdel = {}
	#xavier initializtion 
	model['W1'] = np.random.randn(H, D) / np.sqrt(D)
	model['W2'] = np.random.randn(H) / np.sqrt(H)

grad_buffer = { k: np.zeros_like(v) for k,v in model.iteritems()}
rmsprop_cache = { k : np.zeros_like(v) for k,v in model.iteritems()}


#activation function
def sigmoid(x):
	return 1.0 / (1.0 + np.exp(-x))

def prepro(I):
	I = I[35:195]
	I = I[::2, ::2, 0]
	I = [I == 144] = 0 #remove background colour
	I = [I == 109] = 0
	I[I != 0] = 1 
	return I.astype(np.float).ravel()

def discount_reward(r):
	discounted_r = np.zeros_like(r)
	running_add  = 0
	for t in reversed(xrangd(0, r.size)):
		if r[t] != 0: running_add = 0
		running_add = running_add * gamma +r[t]
		discounted_r[t] = running_add
	return discount_r

def policy_forward(x):
	h = np.dot(model['W1'],x)
	h[h<0] = 0 #RELU
	logp = np.dot(model['W2'], h)
	p = sigmoid(logp)
	return p, h

def policy_backward(eph,epdlogp):
	#eph is array of intermidiate states
	dW2 = np.dot(eph.T, epdlog).ravel()
	dh = np.outer(edplogp, model['W2'])
	dh[eph <= 0] = 0 #RElU
	dW1 = np.dot(dh.T, epx)
	#return both derivaties to update weights
	return {'W1': dW1, 'W2': dW2}

#implemetation details
env = gym.make('Pong-v0')
observation = env.reset()
prev_x = None
xs, hs, dlogps, drs = [], [] ,[] ,[]
running_reward = None
reward_sum = 0
episode_number = 0

# Training
while True:
	cur_x = prepro(observation)
	x = cur_x - prev_x if prev_x is not None else np.zeros(D)
	prev_x = cur_x

	#forward prop
	aprob , h = policy_forward(x)

	#stochastic 
	action = 2 if np.random.uniform() < aprob else 3
	dlog.append(y-aprob)

	#step to env
	env.render()
	observation, reward, done, info = env.step(action)
	reward_sum += reward_sum 
	drs.append(reward)

	if done:
		episode_number += 1

		#stack inputs, hidden states, acctuions , rewards , gradinets
		exp = np.vstack(xs)
		eph = np.vstack(hs)
		epdlogp = np.vstack(dlogps)
		epr = np.vstack(drs)
		xs , hs, dlogp, drs = [], [] , [], []
	#the strength with which we encourage a sampled action is the weighted sum of all rewards afterwards, but later rewards are exponentially less important
	# compute the discounted reward backwards through time
	discounted_epr = discount_rewards(epr)
	# standardize the rewards to be unit normal (helps control the gradient estimator variance)
	discounted_epr -= np.mean(discounted_epr)
	discounted_epr /= np.std(discounted_epr)

	#advatnage - quantity which describes how good the action is compared to the average of all the action.
	epdlogp *= discounted_epr # modulate the gradient with advantage (PG magic happens right here.)
	grad = policy_backward(eph, epdlogp)
	for k in model: grad_buffer[k] += grad[k] # accumulate grad over batch

	# perform rmsprop parameter update every batch_size episodes
	#http://68.media.tumblr.com/2d50e380d8e943afdfd66554d70a84a1/tumblr_inline_o4gfjnL2xK1toi3ym_500.png
	if episode_number % batch_size == 0:
	for k,v in model.iteritems():
		g = grad_buffer[k] # gradient
		rmsprop_cache[k] = decay_rate * rmsprop_cache[k] + (1 - decay_rate) * g**2
		model[k] += learning_rate * g / (np.sqrt(rmsprop_cache[k]) + 1e-5)
		grad_buffer[k] = np.zeros_like(v) # reset batch gradient buffer

	# boring book-keeping
	running_reward = reward_sum if running_reward is None else running_reward * 0.99 + reward_sum * 0.01
	print('resetting env. episode reward total was %f. running mean: %f' % (reward_sum, running_reward))
	if episode_number % 100 == 0: pickle.dump(model, open('save.p', 'wb'))
	reward_sum = 0
	observation = env.reset() # reset env
	prev_x = None

	if reward != 0: # Pong has either +1 or -1 reward exactly when game ends.
	print ('ep %d: game finished, reward: %f' % (episode_number, reward)) + ('' if reward == -1 else ' !!!!!!!!')

