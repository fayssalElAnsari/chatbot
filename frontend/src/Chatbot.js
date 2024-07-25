import React, { useState, useRef } from 'react';
import './Chatbot.css';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';


const Chatbot = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesRef = useRef(messages);

  const chatWithLLM = async (userInput) => {
    const apiEndpoint = 'http://127.0.0.1:8000/chat/v1/stream';

    const data = {
      prompt: userInput,
      max_tokens: 150
    };
    const sse = new EventSource(apiEndpoint + '?query=' + data.prompt);

    sse.onerror = (e) => {
      console.log(e);
      sse.close();
    }

    function getResponseTokens(response) {
      setMessages((prevMessages) => {
        const newMessages = prevMessages.map((message, index) => {
          if (index === prevMessages.length - 1) {
            if (response.type == "PARTIAL_ANSWER") {
              return { ...message, text: message.text + response.content };
            } else if (response.type == "RELEVANT_SOURCES") {
              const newText = "#### RELEVANT SOURCES: \n" + "* " + message.text + response.content.join('\n* ') + "\n\n";
              return { ...message, text: newText };
            }

          }
          return message;
        });
        messagesRef.current = newMessages;
        return newMessages;
      });
    }

    sse.onmessage = e => getResponseTokens(JSON.parse(e.data));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = { text: input, user: true };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    const aiMessage = { text: '', user: false };
    setMessages((prevMessages) => [...prevMessages, aiMessage]);
    chatWithLLM(input);
    setInput('');
  };

  const formatMessageText = (text) => {
    return text.replace(/\n/g, '<br />');
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.user ? 'user-message' : 'ai-message'}`}>
            <ReactMarkdown
              children={message.text}
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      children={String(children).replace(/\n$/, '')}
                      style={atomDark}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    />
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            />

          </div>
        ))}
      </div>
      <form className="chatbot-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default Chatbot;
