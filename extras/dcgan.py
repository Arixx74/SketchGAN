import tensorflow as tf
import numpy as np
import chicken
import datetime
import matplotlib.pyplot as plt
# from tensorflow.examples.tutorials.mnist import input_data

'''
TODO:
	- Implement ezgan and test on MNIST datset
	- Double Check with https://github.com/jonbruner/ezgan
	- Implement batch normalization
	- Modify network architecture + hyperparameters to match GAN256
	or other architectures proven to work
	- Train on sketch images

Things to understand:
	- reeuse of tf variables
	- why gen has batch size and batch norm while discrim doesn't
	- why d_loss_real is calculated with 0.9 instead of 1

Helpul Links:
	https://github.com/llSourcell/Generative_Adversarial_networks_LIVE/blob/master/EZGAN.ipynb
	-> (fto ix cell 4 in jupyter notebook) https://github.com/llSourcell/Generative_Adversarial_networks_LIVE/issues/2
	https://github.com/manicman1999/GAN256/blob/master/main.py

	http://cs231n.github.io/neural-networks-2/
	https://en.wikipedia.org/wiki/Truncated_normal_distribution
	https://stats.stackexchange.com/questions/87248/is-binary-logistic-regression-a-special-case-of-multinomial-logistic-regression#comment609940_87270
	https://datascience.stackexchange.com/questions/9302/the-cross-entropy-error-function-in-neural-networks

	https://www.tensorflow.org/api_docs/python/tf/reshape
'''

class DCGAN:

	def __init__(self):

		# self.mnist = input_data.read_data_sets("MNIST_data/")
		
		self.sketch_dataset = chicken.DataSet(self.load_data())

		
		self.iterations = 100000
		self.load_from_ckpt = 57000

		self.batch_size = 16
		self.z_dimensions = 4096
		self.learning_rate = 0.0001

	def load_data(self):

		print('Loading Data...')
		images = chicken.get_images('data/')
		data2d = chicken.grayscale_to_2d(images)
		data2d = np.reshape(data2d, (-1, 256, 256, 1))
		data2d = np.array(data2d, dtype=np.float32)
		data2d = data2d / 255
		print('shape:',data2d.shape)
		# print('sample image:', data2d[0])
		print('Data Loaded.')
		return data2d

	def discriminator(self, x_image, reuse=False):

		if(reuse):
			tf.get_variable_scope().reuse_variables()

		# Convolutional Block 1
		# 8, 3x3 filters
		d_w1 = tf.get_variable('d_w1', [3, 3, 1, 8], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b1 = tf.get_variable('d_b1', [8], initializer=tf.constant_initializer(0))
		d1 = tf.nn.conv2d(input=x_image, filter=d_w1, strides=[1, 1, 1, 1], padding='SAME')
		d1 = d1 + d_b1
		d1 = tf.nn.leaky_relu(d1, alpha=0.2)
		d1 = tf.nn.dropout(d1, keep_prob=0.25)
		d1 = tf.nn.avg_pool(d1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

		# Convolutional Block 2
		# 16, 3x3 filters
		d_w2 = tf.get_variable('d_w2', [3, 3, 8, 16], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b2 = tf.get_variable('d_b2', [16], initializer=tf.constant_initializer(0))
		d2 = tf.nn.conv2d(input=d1, filter=d_w2, strides=[1, 1, 1, 1], padding="SAME")
		d2 = d2 + d_b2
		d2 = tf.nn.leaky_relu(d2, alpha=0.2)
		d2 = tf.nn.dropout(d2, keep_prob=0.25)
		d2 = tf.nn.avg_pool(d2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

		# Convolutional Block 3
		# 32, 3x3 filters
		d_w3 = tf.get_variable('d_w3', [3, 3, 16, 32], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b3 = tf.get_variable('d_b3', [32], initializer=tf.constant_initializer(0))
		d3 = tf.nn.conv2d(input=d2, filter=d_w3, strides=[1, 1, 1, 1], padding="SAME")
		d3 = d3 + d_b3
		d3 = tf.nn.leaky_relu(d3, alpha=0.2)
		d3 = tf.nn.dropout(d3, keep_prob=0.25)
		d3 = tf.nn.avg_pool(d3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

		# Convolutional Block 4
		# 64, 3x3 filters
		d_w4 = tf.get_variable('d_w4', [3, 3, 32, 64], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b4 = tf.get_variable('d_b4', [64], initializer=tf.constant_initializer(0))
		d4 = tf.nn.conv2d(input=d3, filter=d_w4, strides=[1, 1, 1, 1], padding="SAME")
		d4 = d4 + d_b4
		d4 = tf.nn.leaky_relu(d4, alpha=0.2)
		d4 = tf.nn.dropout(d4, keep_prob=0.25)
		d4 = tf.nn.avg_pool(d4, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

		# Convolutional Block 5
		# 128, 3x3 filters
		d_w5 = tf.get_variable('d_w5', [3, 3, 64, 128], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b5 = tf.get_variable('d_b5', [128], initializer=tf.constant_initializer(0))
		d5 = tf.nn.conv2d(input=d4, filter=d_w5, strides=[1, 1, 1, 1], padding="SAME")
		d5 = d5 + d_b5
		d5 = tf.nn.leaky_relu(d5, alpha=0.2)
		d5 = tf.nn.dropout(d5, keep_prob=0.25)
		d5 = tf.nn.avg_pool(d5, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

		# Convolutional Block 6
		# 256, 3x3 filters
		d_w6 = tf.get_variable('d_w6', [3, 3, 128, 256], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b6 = tf.get_variable('d_b6', [256], initializer=tf.constant_initializer(0))
		d6 = tf.nn.conv2d(input=d5, filter=d_w6, strides=[1, 1, 1, 1], padding="SAME")
		d6 = d6 + d_b6
		d6 = tf.nn.leaky_relu(d6, alpha=0.2)
		d6 = tf.nn.dropout(d6, keep_prob=0.25)
		d6 = tf.nn.avg_pool(d6, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

		# Fully connected layer 1
		d_w7 = tf.get_variable('d_w7', [4 * 4 * 256, 128], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b7 = tf.get_variable('d_b7', [128], initializer=tf.constant_initializer(0))
		d7 = tf.reshape(d6, [-1, 4 * 4 * 256])
		d7 = tf.matmul(d7, d_w7)
		d7 = d7 + d_b7
		d7 = tf.nn.leaky_relu(d7)

		# Fully connected layer 2
		d_w8 = tf.get_variable('d_w8', [128, 1], initializer=tf.truncated_normal_initializer(stddev=0.02))
		d_b8 = tf.get_variable('d_b8', [1], initializer=tf.constant_initializer(0))
		d8 = tf.matmul(d7, d_w8)
		d8 = d8 + d_b8

		# dimensions of output tensor: batchsize x 1
		# (binary classification)
		return d8

	def generator(self, batch_size, z_dim):
		z = tf.truncated_normal([batch_size, z_dim], mean=0, stddev=1, name='z')

		g_w1 = tf.get_variable('g_w1', [z_dim, 4096], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b1 = tf.get_variable('g_b1', [4096], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g1 = tf.matmul(z, g_w1) + g_b1
		g1 = tf.reshape(g1, [-1, 4, 4, 256])
		g1 = tf.contrib.layers.batch_norm(g1, epsilon=1e-5, scope='bn1')
		g1 = tf.nn.relu(g1)

		# filter syntax: [filter_height, filter_width, in_channels, out_channels]
		g_w2 = tf.get_variable('g_w2', [3, 3, 256, 256], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b2 = tf.get_variable('g_b2', [256], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g2 = tf.nn.conv2d(g1, g_w2, strides=[1, 2, 2, 1], padding='SAME')
		g2 = g2 + g_b2
		g2 = tf.contrib.layers.batch_norm(g2, epsilon=1e-5, scope='bn2')
		g2 = tf.nn.relu(g2)
		g2 = tf.image.resize_images(g2, [8, 8])

		g_w3 = tf.get_variable('g_w3', [3, 3, 256, 128], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b3 = tf.get_variable('g_b3', [128], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g3 = tf.nn.conv2d(g2, g_w3, strides=[1, 2, 2, 1], padding='SAME')
		g3 = g3 + g_b3
		g3 = tf.contrib.layers.batch_norm(g3, epsilon=1e-5, scope='bn3')
		g3 = tf.nn.relu(g3)
		g3 = tf.image.resize_images(g3, [16, 16])

		g_w4 = tf.get_variable('g_w4', [3, 3, 128, 64], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b4 = tf.get_variable('g_b4', [64], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g4 = tf.nn.conv2d(g3, g_w4, strides=[1, 2, 2, 1], padding='SAME')
		g4 = g4 + g_b4
		g4 = tf.contrib.layers.batch_norm(g4, epsilon=1e-5, scope='bn4')
		g4 = tf.nn.relu(g4)
		g4 = tf.image.resize_images(g4, [32, 32])

		g_w5 = tf.get_variable('g_w5', [3, 3, 64, 32], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b5 = tf.get_variable('g_b5', [32], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g5 = tf.nn.conv2d(g4, g_w5, strides=[1, 2, 2, 1], padding='SAME')
		g5 = g5 + g_b5
		g5 = tf.contrib.layers.batch_norm(g5, epsilon=1e-5, scope='bn5')
		g5 = tf.nn.relu(g5)
		g5 = tf.image.resize_images(g5, [64, 64])

		g_w6 = tf.get_variable('g_w6', [3, 3, 32, 16], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b6 = tf.get_variable('g_b6', [16], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g6 = tf.nn.conv2d(g5, g_w6, strides=[1, 2, 2, 1], padding='SAME')
		g6 = g6 + g_b6
		g6 = tf.contrib.layers.batch_norm(g6, epsilon=1e-5, scope='bn6')
		g6 = tf.nn.relu(g6)
		g6 = tf.image.resize_images(g6, [128, 128])

		g_w7 = tf.get_variable('g_w7', [3, 3, 16, 8], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b7 = tf.get_variable('g_b7', [8], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g7 = tf.nn.conv2d(g6, g_w7, strides=[1, 2, 2, 1], padding='SAME')
		g7 = g7 + g_b7
		g7 = tf.contrib.layers.batch_norm(g7, epsilon=1e-5, scope='bn7')
		g7 = tf.nn.relu(g7)
		g7 = tf.image.resize_images(g7, [256, 256])

		g_w8 = tf.get_variable('g_w8', [3, 3, 8, 1], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
		g_b8 = tf.get_variable('g_b8', [1], initializer=tf.truncated_normal_initializer(stddev=0.02))
		g8 = tf.nn.conv2d(g7, g_w8, strides=[1, 1, 1, 1], padding='SAME')
		# g8 = tf.nn.conv2d(g7, g_w8, strides=[1, 2, 2, 1], padding='SAME')
		g8 = g8 + g_b8
		g8 = tf.sigmoid(g8) # no batch norm, but sigmoid for crisper images

		# dimensions of output tensor: batch_size x 256 x 256 x 1
		# changed from 3 to 1 channels
		return g8

	def run_session(self):

		sess = tf.Session()
		
		x_placeholder = tf.placeholder('float', shape=[None, 256, 256, 1], name='x_placeholder')
		# G(z)
		Gz = self.generator(self.batch_size, self.z_dimensions)
		# D(x)
		Dx = self.discriminator(x_placeholder)

		with tf.variable_scope(tf.get_variable_scope()) as scope:
			pass

		# D(G(z))
		Dg = self.discriminator(Gz, reuse=True)
		g_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=Dg, labels=tf.ones_like(Dg)))
		d_loss_real = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=Dx, labels=tf.fill([self.batch_size, 1], 0.9)))
		d_loss_fake = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=Dg, labels=tf.zeros_like(Dg)))
		d_loss = d_loss_real + d_loss_fake

		# get lists of variables to optimize for generator and discriminator
		tvars = tf.trainable_variables()
		d_vars = [var for var in tvars if 'd_' in var.name]
		g_vars = [var for var in tvars if 'g_' in var.name]


		with tf.variable_scope(scope):
			d_trainer_fake = tf.train.AdamOptimizer(self.learning_rate).minimize(d_loss_fake, var_list=d_vars)
			d_trainer_real = tf.train.AdamOptimizer(self.learning_rate).minimize(d_loss_real, var_list=d_vars)
			g_trainer = tf.train.AdamOptimizer(self.learning_rate).minimize(g_loss, var_list=g_vars)

		tf.summary.scalar('Generator_loss', g_loss)
		tf.summary.scalar('Discriminator_loss_real', d_loss_real)
		tf.summary.scalar('Discriminator_loss_fake', d_loss_fake)

		d_real_count_ph = tf.placeholder(tf.float32)
		d_fake_count_ph = tf.placeholder(tf.float32)
		g_count_ph = tf.placeholder(tf.float32)

		tf.summary.scalar('d_real_count', d_real_count_ph)
		tf.summary.scalar('d_fake_count', d_fake_count_ph)
		tf.summary.scalar('g_count', g_count_ph)

		# Check how discriminator is doing on generated and real images
		d_on_generated = tf.reduce_mean(self.discriminator(self.generator(self.batch_size, self.z_dimensions)))
		d_on_real = tf.reduce_mean(self.discriminator(x_placeholder))

		tf.summary.scalar('d_on_generated_eval', d_on_generated)
		tf.summary.scalar('d_on_real_eval', d_on_real)

		images_for_tensorboard = self.generator(self.batch_size, self.z_dimensions)
		tf.summary.image('Generated_images', images_for_tensorboard, 10)
		merged = tf.summary.merge_all()
		logdir = 'tensorboard/gan/'
		writer = tf.summary.FileWriter(logdir, sess.graph)
		print(logdir)



		self.saver = tf.train.Saver()
		
		sess.run(tf.global_variables_initializer())

		if self.load_from_ckpt:
			self.load(sess, 'models/pretrained_gan.ckpt-' + str(self.load_from_ckpt))
		
		gLoss = 0
		dLossFake, dLossReal = 1, 1
		d_real_count, d_fake_count, g_count = 0, 0, 0

		for i in range(self.load_from_ckpt, self.iterations):
			real_image_batch = self.sketch_dataset.next_batch(self.batch_size)
			if dLossFake > 0.6:
				# train discriminator on generated images
				_, dLossReal, dLossFake, gLoss = sess.run([d_trainer_fake, d_loss_real, d_loss_fake, g_loss], {x_placeholder: real_image_batch})

				d_fake_count += 1

			if gLoss > 0.5:
				# train the generator
				_, dLossReal, dLossFake, gLoss = sess.run([g_trainer, d_loss_real, d_loss_fake, g_loss], {x_placeholder: real_image_batch})

				g_count += 1

			if dLossReal > 0.45:

				# _, dLossReal, dLossFake, gLoss = sess.run([d_trainer_real, d_loss_real, d_loss_fake, gLoss],
				# 											 {x_placeholder: real_image_batch})

				_, dLossReal, dLossFake, gLoss = sess.run([d_trainer_real, d_loss_real, d_loss_fake, g_loss],
                                                    {x_placeholder: real_image_batch})

				d_real_count += 1

			# if i % 10 == 0:
				# real_image_batch = self.mnist.validation.next_batch(self.batch_size)[0].reshape([self.batch_size, 28, 28, 1])
				# summary = sess.run(merged, {x_placeholder: real_image_batch, d_real_count_ph: d_real_count,
				# 							d_fake_count_ph: d_fake_count, g_count_ph: g_count})

				# writer.add_summary(summary, i)
				# d_real_count, d_fake_count, g_count = 0, 0, 0

			if i % 1000 == 0:
				images = sess.run(self.generator(3, self.z_dimensions))
				d_result = sess.run(self.discriminator(x_placeholder), {x_placeholder: images})
				print('TRAINING STEP', i, 'AT', datetime.datetime.now())
				for j in range(1):
					print('Discriminator classification', d_result[j])
					# im = 1-images[j, :, :, 0]
					# plt.imshow(im.reshape([28, 28]), cmap='Greys')
					# plt.ion()
					# plt.imshow(im, cmap='Greys')
					# plt.show()
					# plt.plot(im)
					# plt.draw()
					# plt.show(block=False)

			# if i == 15000:
			# 	images = sess.run(self.generator(3, self.z_dimensions))
			# 	d_result = sess.run(self.discriminator(x_placeholder), {x_placeholder: images})
			# 	for j in range(3):
			# 		print('Discriminator classificationnnnnnnnnn', d_result[j])
			# 		im = 1-images[j, :, :, 0]
			# 		plt.imshow(im.reshape([28, 28]), cmap='Greys')
			# 		plt.show()


			if i % 1000 == 0:
				# save_path = saver.save(sess, 'models/pretrained_gan.ckpt', global_step=i)
				# print('Saved to %s' % save_path)
				if i != self.load_from_ckpt:
					self.save(sess, 'models/pretrained_gan.ckpt', i)

		test_images = sess.run(self.generator(10, self.z_dimensions))
		test_eval = sess.run(self.discriminator(x_placeholder), {x_placeholder: test_images})

		# real_images = self.mnist.validation.next_batch(10)[0].reshape([10, 28, 28, 1])
		# real_eval = sess.run(self.discriminator(x_placeholder), {x_placeholder: real_images})

		rib = self.sketch_dataset.next_batch(self.batch_size)
		_, dLossReal, dLossFake, gLoss = sess.run([g_trainer, d_loss_real, d_loss_fake, g_loss], {x_placeholder: rib})
		print(dLossReal)
		print(dLossFake)
		print(gLoss)
		
		# display images and show discriminator's probabilities
		for i in range(10):
			# print(test_eval[i])
			# print(test_images[i])
			plt.imshow(1-test_images[i, :, :, 0], cmap='Greys')
			plt.show()
		

		# chicken.display_all(np.reshape(test_images, (-1, 256, 256)))
		# chicken.display_all(np.reshape(self.sketch_dataset.next_batch(10), (-1, 256, 256)))

		# asdf = self.sketch_dataset.next_batch(10)
		# for i in range(10):
		# 	print(asdf[i])
		# 	plt.imshow(1-asdf[i, :, :, 0], cmap='Greys')
		# 	plt.show()

		# # Now do the same for real MNIST images
		# for i in range(10):
		#     print(real_eval[i])
		#     plt.imshow(real_images[i, :, :, 0], cmap='Greys')
		#     plt.show()

	def save(self, sess, dir, iteration):
		save_path = self.saver.save(sess, dir, global_step=iteration)
		print('Saved to %s' % save_path)
		return

	def load(self, sess, prefix):
		self.saver.restore(sess, prefix)
		print("Model restored.")
		return

gan = DCGAN()
gan.run_session()

