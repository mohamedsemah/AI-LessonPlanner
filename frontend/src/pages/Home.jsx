import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, BookOpen, Target, Brain, Sparkles, CheckCircle, Users, Clock, Download } from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';

const Home = () => {
  const features = [
    {
      icon: Target,
      title: 'Bloom\'s Taxonomy Integration',
      description: 'Generate learning objectives across all cognitive levels with AI-powered precision.',
      color: 'text-red-500'
    },
    {
      icon: Brain,
      title: 'Gagne\'s Nine Events',
      description: 'Structured lesson plans following proven instructional design principles.',
      color: 'text-blue-500'
    },
    {
      icon: Sparkles,
      title: 'AI-Powered Generation',
      description: 'Advanced GPT-4o integration for intelligent content creation.',
      color: 'text-purple-500'
    },
    {
      icon: BookOpen,
      title: 'Editable Content',
      description: 'Rich text editor for customizing and refining generated content.',
      color: 'text-green-500'
    },
    {
      icon: Download,
      title: 'Professional Export',
      description: 'Export polished lesson plans as formatted PDF documents.',
      color: 'text-indigo-500'
    },
    {
      icon: Clock,
      title: 'Time Management',
      description: 'Automatic duration allocation across instructional events.',
      color: 'text-orange-500'
    }
  ];

  const steps = [
    {
      number: '01',
      title: 'Input Lesson Details',
      description: 'Provide course information, learning objectives, and select Bloom\'s taxonomy levels.'
    },
    {
      number: '02',
      title: 'AI Generation',
      description: 'Our AI creates detailed objectives, lesson plans, and Gagne\'s nine events structure.'
    },
    {
      number: '03',
      title: 'Review & Refine',
      description: 'Edit and customize the generated content using our rich text editor.'
    },
    {
      number: '04',
      title: 'Export & Use',
      description: 'Download your professional lesson plan as a formatted PDF document.'
    }
  ];

  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="relative py-20 sm:py-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight">
                <span className="bg-gradient-to-r from-primary-600 via-purple-600 to-secondary-600 bg-clip-text text-transparent">
                  AI-Powered
                </span>
                <br />
                <span className="text-gray-900">
                  Lesson Planning
                </span>
              </h1>

              <p className="mt-6 max-w-2xl mx-auto text-lg sm:text-xl text-gray-600 leading-relaxed">
                Generate comprehensive lesson plans using Bloom's Taxonomy and Gagne's Nine Events of Instruction.
                Perfect for college educators who want to create engaging, pedagogically sound lessons.
              </p>
            </motion.div>

            <motion.div
              className="mt-10 flex flex-col sm:flex-row gap-4 justify-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Link to="/create">
                <Button size="lg" className="w-full sm:w-auto">
                  Create Your First Lesson
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>

              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                <BookOpen className="w-5 h-5 mr-2" />
                Learn More
              </Button>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Educators
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to create professional, pedagogically sound lesson plans
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card hover className="h-full">
                    <CardContent className="p-6">
                      <div className={`w-12 h-12 rounded-lg bg-gray-50 flex items-center justify-center mb-4 ${feature.color}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Create professional lesson plans in just four simple steps
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                className="text-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mx-auto shadow-soft">
                    <span className="text-2xl font-bold text-white">
                      {step.number}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="hidden lg:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-primary-200 to-gray-200 transform -translate-y-0.5" />
                  )}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-600">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary-600 to-primary-700">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Ready to Transform Your Teaching?
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Join educators who are already creating better lessons with AI assistance
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/create">
                <Button size="lg" variant="secondary" className="w-full sm:w-auto">
                  Start Creating Now
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>

            <div className="mt-8 flex items-center justify-center gap-8 text-primary-100">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                <span>Free to use</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                <span>No registration required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                <span>Instant results</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;