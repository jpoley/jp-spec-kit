# jpspec Workflow System

**Take your ideas from research to production with AI-powered multi-agent orchestration**

jpspec is a comprehensive workflow system that orchestrates specialized AI agents to transform ideas into production-ready software. It guides you through research, specification, architecture, implementation, validation, and operations—handling the complexity of modern software delivery while maintaining quality and security standards.

## Table of Contents

- [Why jpspec?](#why-jpspec)
- [Quick Start](#quick-start)
- [Complete Workflow Example](#complete-workflow-example)
- [Command Reference](#command-reference)
- [Multi-Agent Architecture](#multi-agent-architecture)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Why jpspec?

Building production-ready software requires expertise across multiple domains: product management, architecture, frontend, backend, security, testing, operations, and more. jpspec brings together specialized AI agents that work together seamlessly, enabling you to:

- **Move faster**: Parallel agent execution accelerates delivery
- **Maintain quality**: Built-in code review, security scanning, and QA validation
- **Follow best practices**: Agents apply industry-standard patterns (DORA metrics, Enterprise Integration Patterns, WCAG 2.1 AA, etc.)
- **Reduce errors**: Sequential validation gates catch issues early
- **Scale expertise**: Access specialized knowledge across the full software lifecycle

### What jpspec Does

jpspec automates the software delivery lifecycle through six specialized workflows:

1. **Research** - Market analysis, competitive landscape, technical feasibility
2. **Specify** - Comprehensive product requirements and task breakdown
3. **Plan** - System architecture and platform infrastructure design
4. **Implement** - Multi-tier development with integrated code review
5. **Validate** - QA testing, security assessment, documentation, release management
6. **Operate** - CI/CD, Kubernetes, observability, incident management

---

## Quick Start

**Build a simple REST API in 5 steps:**

```bash
# 1. Research the market and validate the idea
/jpspec:research Build a task management REST API

# 2. Create product specifications
/jpspec:specify Task management REST API with authentication

# 3. Design architecture and platform
/jpspec:plan Task management REST API

# 4. Implement the backend
/jpspec:implement Task management REST API backend

# 5. Validate and prepare for release
/jpspec:validate Task management REST API

# 6. (Optional) Set up operations infrastructure
/jpspec:operate Task management REST API
```

Each command launches specialized AI agents that collaborate to complete that phase of development.

---

## Complete Workflow Example

**Project: AI-Powered Customer Service Chatbot**

Let's walk through building a production-grade customer service chatbot from concept to deployment.

### Step 1: Research and Business Validation

**Command:**
```bash
/jpspec:research AI-powered customer service chatbot with sentiment analysis and multi-language support
```

**What happens:**
- **Researcher agent** analyzes the market, competitive landscape, technical feasibility, and industry trends
- **Business-validator agent** evaluates market opportunity (TAM/SAM/SOM), financial viability, operational feasibility, and provides a Go/No-Go recommendation

**Deliverables:**
- Research report with market analysis and competitive landscape
- Business validation report with opportunity score and risk register
- Recommendation on whether to proceed

**Output example:**
```
RESEARCH FINDINGS:
Market Size: $15B (growing 25% YoY)
Key Competitors: Intercom, Drift, Zendesk
Technical Stack: LLMs (GPT-4, Claude), speech-to-text APIs, sentiment analysis
Recommendation: STRONG GO (Score: 8.5/10)
```

---

### Step 2: Product Specification

**Command:**
```bash
/jpspec:specify AI customer service chatbot based on research findings
```

**What happens:**
- **Product-requirements-manager-enhanced agent** creates a comprehensive Product Requirement Document (PRD)
- Generates user stories, acceptance criteria, task breakdown, and success metrics
- Populates `/speckit.tasks` with prioritized backlog

**Deliverables:**
- Complete PRD with functional and non-functional requirements
- User personas and journey maps
- Task breakdown organized by epic
- Success metrics and KPIs

**Output includes:**
```markdown
## Executive Summary
Problem: 70% of customer inquiries are repetitive, overwhelming support teams
Solution: AI chatbot that handles tier-1 support with 24/7 availability
Success Metrics: 60% inquiry resolution rate, <2s response time, 85% CSAT

## User Stories
- As a customer, I want instant answers to common questions so I can resolve issues quickly
- As a support agent, I want the chatbot to handle simple queries so I can focus on complex issues
- As a manager, I want analytics on chatbot performance so I can optimize support quality

## Functional Requirements
- Natural language understanding with multi-turn conversations
- Sentiment analysis with automatic escalation for frustrated customers
- Multi-language support (English, Spanish, French, German)
- Knowledge base integration
- Human handoff capability
...
```

---

### Step 3: Architecture and Platform Planning

**Command:**
```bash
/jpspec:plan AI customer service chatbot
```

**What happens:**
- **Software-architect-enhanced agent** designs system architecture, component boundaries, integration patterns, and ADRs (Architecture Decision Records)
- **Platform-engineer-enhanced agent** designs CI/CD pipelines, Kubernetes architecture, observability stack, and security integration
- Both agents run **in parallel** for efficiency
- Results are consolidated into `/speckit.constitution`

**Deliverables:**
- System architecture diagrams and component design
- Architecture Decision Records (ADRs) for key choices
- Platform infrastructure design
- CI/CD pipeline architecture
- Updated `/speckit.constitution` with principles and standards

**Output includes:**
```markdown
## System Architecture

### Components
1. **API Gateway** (Kong/Traefik)
2. **Conversation Service** (Go)
   - Intent classification
   - Dialog management
   - Context tracking
3. **LLM Integration Service** (Python)
   - GPT-4 API client
   - Prompt engineering
   - Response streaming
4. **Sentiment Analysis Service** (Python + Hugging Face)
5. **Knowledge Base Service** (vector DB: Pinecone/Weaviate)
6. **Escalation Service** (Node.js)

### Integration Patterns
- **API Gateway Pattern**: Single entry point for all clients
- **Event-Driven Architecture**: Kafka for async events
- **Saga Pattern**: Distributed transaction management
- **Circuit Breaker**: Resilience against LLM API failures

## ADR-001: LLM Provider Selection
Context: Need reliable, performant LLM with multi-language support
Decision: Use OpenAI GPT-4 with Claude as fallback
Rationale: Best accuracy, streaming support, 99.9% SLA
Consequences: Vendor lock-in risk, cost considerations
...
```

---

### Step 4: Implementation

**Command:**
```bash
/jpspec:implement AI customer service chatbot
```

**What happens:**
- Multiple specialized engineers work **in parallel**:
  - **Frontend-engineer agent**: Builds chat widget UI with React/TypeScript
  - **Backend-engineer agent**: Implements API services in Go/Python
  - **AI-ml-engineer agent**: Develops sentiment analysis model and LLM integration
- After implementation completes, code review agents run **sequentially**:
  - **Frontend-code-reviewer agent**: Reviews UI code for performance, accessibility, security
  - **Backend-code-reviewer agent**: Reviews API code for security, performance, code quality

**Deliverables:**
- Production-ready frontend code (React/TypeScript)
- Backend services (Go for API gateway, Python for ML services)
- Sentiment analysis model with training pipeline
- Comprehensive test suites (unit, integration, E2E)
- Code review reports with categorized feedback

**Output includes:**

*Frontend Implementation:*
```typescript
// src/components/ChatWidget.tsx
import React, { useState, useCallback } from 'react';
import { useChatMessages } from '../hooks/useChatMessages';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { WCAG } from '../utils/accessibility';

export const ChatWidget: React.FC = () => {
  const { messages, sendMessage, isLoading } = useChatMessages();
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = useCallback(async () => {
    if (!inputValue.trim()) return;
    await sendMessage(inputValue);
    setInputValue('');
  }, [inputValue, sendMessage]);

  return (
    <div
      className="chat-widget"
      role="region"
      aria-label="Customer service chat"
      {...WCAG.ariaLive('polite')}
    >
      <MessageList messages={messages} />
      <ChatInput
        value={inputValue}
        onChange={setInputValue}
        onSubmit={handleSubmit}
        disabled={isLoading}
        aria-label="Type your message"
      />
    </div>
  );
};
```

*Backend Implementation:*
```go
// internal/conversation/service.go
package conversation

import (
    "context"
    "time"
    "github.com/chatbot/internal/llm"
    "github.com/chatbot/internal/sentiment"
)

type Service struct {
    llmClient       llm.Client
    sentimentClient sentiment.Analyzer
    repo            Repository
}

func (s *Service) ProcessMessage(ctx context.Context, req MessageRequest) (*MessageResponse, error) {
    // Validate input
    if err := req.Validate(); err != nil {
        return nil, ErrInvalidInput
    }

    // Analyze sentiment
    sentimentScore, err := s.sentimentClient.Analyze(ctx, req.Message)
    if err != nil {
        return nil, err
    }

    // Check if escalation needed
    if sentimentScore < -0.7 {
        return s.escalateToHuman(ctx, req)
    }

    // Get LLM response
    response, err := s.llmClient.Chat(ctx, llm.ChatRequest{
        Messages: s.buildContext(req),
        Temperature: 0.7,
        MaxTokens: 500,
    })
    if err != nil {
        return nil, err
    }

    // Store conversation
    if err := s.repo.SaveMessage(ctx, req, response); err != nil {
        return nil, err
    }

    return &MessageResponse{
        Message: response.Content,
        Sentiment: sentimentScore,
        RequiresEscalation: false,
    }, nil
}
```

*ML Model Implementation:*
```python
# ml_services/sentiment_analyzer.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List
import mlflow
import logging

class SentimentAnalyzer:
    """Production sentiment analysis model with MLOps integration."""

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        self.logger = logging.getLogger(__name__)

        # MLflow tracking
        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("sentiment-analysis-production")

    def analyze(self, text: str) -> float:
        """
        Analyze sentiment of input text.

        Args:
            text: Input message text

        Returns:
            Sentiment score from -1.0 (very negative) to 1.0 (very positive)
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)

            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)

            # Convert to score (-1 to 1)
            # Assuming binary classification: [negative, positive]
            negative_prob = probabilities[0][0].item()
            positive_prob = probabilities[0][1].item()
            sentiment_score = positive_prob - negative_prob

            # Log prediction to MLflow
            mlflow.log_metric("sentiment_score", sentiment_score)

            self.logger.info(f"Sentiment analyzed: {sentiment_score:.3f}")
            return sentiment_score

        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            raise

    def batch_analyze(self, texts: List[str]) -> List[float]:
        """Batch process multiple texts for efficiency."""
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)

        scores = (probabilities[:, 1] - probabilities[:, 0]).cpu().numpy().tolist()
        return scores
```

*Test Suites:*

**Unit Tests (Frontend):**
```typescript
// src/components/__tests__/ChatWidget.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatWidget } from '../ChatWidget';
import { useChatMessages } from '../../hooks/useChatMessages';

vi.mock('../../hooks/useChatMessages');

describe('ChatWidget', () => {
  const mockSendMessage = vi.fn();

  beforeEach(() => {
    vi.mocked(useChatMessages).mockReturnValue({
      messages: [
        { id: '1', text: 'Hello', sender: 'user', timestamp: new Date() },
        { id: '2', text: 'Hi! How can I help?', sender: 'bot', timestamp: new Date() }
      ],
      sendMessage: mockSendMessage,
      isLoading: false
    });
  });

  it('should render messages correctly', () => {
    render(<ChatWidget />);

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi! How can I help?')).toBeInTheDocument();
  });

  it('should send message on submit', async () => {
    const user = userEvent.setup();
    render(<ChatWidget />);

    const input = screen.getByLabelText('Type your message');
    const submitButton = screen.getByRole('button', { name: /send/i });

    await user.type(input, 'Test message');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith('Test message');
    });
  });

  it('should clear input after sending', async () => {
    const user = userEvent.setup();
    render(<ChatWidget />);

    const input = screen.getByLabelText('Type your message') as HTMLInputElement;

    await user.type(input, 'Test message');
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });

  it('should disable input while loading', () => {
    vi.mocked(useChatMessages).mockReturnValue({
      messages: [],
      sendMessage: mockSendMessage,
      isLoading: true
    });

    render(<ChatWidget />);

    const input = screen.getByLabelText('Type your message');
    expect(input).toBeDisabled();
  });

  it('should be keyboard accessible', async () => {
    const user = userEvent.setup();
    render(<ChatWidget />);

    // Tab to input
    await user.tab();
    expect(screen.getByLabelText('Type your message')).toHaveFocus();

    // Type and submit with Enter
    await user.keyboard('Test message{Enter}');

    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalled();
    });
  });
});
```

**Integration Tests (Backend):**
```go
// internal/conversation/service_test.go
package conversation_test

import (
    "context"
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/chatbot/internal/conversation"
    "github.com/chatbot/internal/llm"
    "github.com/chatbot/internal/sentiment"
)

type MockLLMClient struct {
    mock.Mock
}

func (m *MockLLMClient) Chat(ctx context.Context, req llm.ChatRequest) (*llm.ChatResponse, error) {
    args := m.Called(ctx, req)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*llm.ChatResponse), args.Error(1)
}

type MockSentimentAnalyzer struct {
    mock.Mock
}

func (m *MockSentimentAnalyzer) Analyze(ctx context.Context, text string) (float64, error) {
    args := m.Called(ctx, text)
    return args.Get(0).(float64), args.Error(1)
}

func TestProcessMessage_HappyPath(t *testing.T) {
    // Setup
    mockLLM := new(MockLLMClient)
    mockSentiment := new(MockSentimentAnalyzer)
    mockRepo := new(MockRepository)

    svc := conversation.NewService(mockLLM, mockSentiment, mockRepo)

    // Mock responses
    mockSentiment.On("Analyze", mock.Anything, "Hello").Return(0.5, nil)
    mockLLM.On("Chat", mock.Anything, mock.AnythingOfType("llm.ChatRequest")).
        Return(&llm.ChatResponse{Content: "Hi! How can I help?"}, nil)
    mockRepo.On("SaveMessage", mock.Anything, mock.Anything, mock.Anything).Return(nil)

    // Execute
    req := conversation.MessageRequest{
        Message: "Hello",
        UserID:  "user123",
    }

    resp, err := svc.ProcessMessage(context.Background(), req)

    // Assert
    assert.NoError(t, err)
    assert.NotNil(t, resp)
    assert.Equal(t, "Hi! How can I help?", resp.Message)
    assert.Equal(t, 0.5, resp.Sentiment)
    assert.False(t, resp.RequiresEscalation)

    mockSentiment.AssertExpectations(t)
    mockLLM.AssertExpectations(t)
    mockRepo.AssertExpectations(t)
}

func TestProcessMessage_NegativeSentimentEscalation(t *testing.T) {
    // Setup
    mockLLM := new(MockLLMClient)
    mockSentiment := new(MockSentimentAnalyzer)
    mockRepo := new(MockRepository)

    svc := conversation.NewService(mockLLM, mockSentiment, mockRepo)

    // Mock very negative sentiment
    mockSentiment.On("Analyze", mock.Anything, "I'm very frustrated!").Return(-0.85, nil)
    mockRepo.On("CreateEscalation", mock.Anything, mock.Anything).Return(nil)

    // Execute
    req := conversation.MessageRequest{
        Message: "I'm very frustrated!",
        UserID:  "user123",
    }

    resp, err := svc.ProcessMessage(context.Background(), req)

    // Assert
    assert.NoError(t, err)
    assert.True(t, resp.RequiresEscalation)

    // LLM should NOT be called for escalations
    mockLLM.AssertNotCalled(t, "Chat")
}

func TestProcessMessage_InvalidInput(t *testing.T) {
    svc := conversation.NewService(nil, nil, nil)

    req := conversation.MessageRequest{
        Message: "", // Empty message
        UserID:  "user123",
    }

    _, err := svc.ProcessMessage(context.Background(), req)

    assert.Error(t, err)
    assert.Equal(t, conversation.ErrInvalidInput, err)
}
```

**E2E Tests:**
```typescript
// e2e/chatbot.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Customer Service Chatbot E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should handle complete conversation flow', async ({ page }) => {
    // Wait for chat widget to load
    await expect(page.getByRole('region', { name: 'Customer service chat' })).toBeVisible();

    // Send first message
    const input = page.getByLabel('Type your message');
    await input.fill('Hello, I need help with my order');
    await input.press('Enter');

    // Verify message appears
    await expect(page.getByText('Hello, I need help with my order')).toBeVisible();

    // Wait for bot response
    await expect(page.getByText(/I'd be happy to help/i)).toBeVisible({ timeout: 5000 });

    // Send follow-up
    await input.fill('Order number 12345');
    await input.press('Enter');

    // Verify bot processes order lookup
    await expect(page.getByText(/Looking up order/i)).toBeVisible({ timeout: 5000 });
  });

  test('should escalate frustrated customer', async ({ page }) => {
    const input = page.getByLabel('Type your message');

    // Send frustrated message
    await input.fill("This is terrible service! I'm very angry!");
    await input.press('Enter');

    // Verify escalation message
    await expect(page.getByText(/connecting you with a human agent/i))
      .toBeVisible({ timeout: 5000 });

    // Verify escalation indicator
    await expect(page.getByTestId('escalation-badge')).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Tab to input
    await page.keyboard.press('Tab');

    // Verify input has focus
    const input = page.getByLabel('Type your message');
    await expect(input).toBeFocused();

    // Type and submit with keyboard
    await page.keyboard.type('Test message');
    await page.keyboard.press('Enter');

    // Verify message sent
    await expect(page.getByText('Test message')).toBeVisible();
  });

  test('should handle network errors gracefully', async ({ page, context }) => {
    // Simulate offline
    await context.setOffline(true);

    const input = page.getByLabel('Type your message');
    await input.fill('Test message');
    await input.press('Enter');

    // Verify error message
    await expect(page.getByText(/Unable to connect/i)).toBeVisible();

    // Restore connection
    await context.setOffline(false);

    // Retry should work
    await page.getByRole('button', { name: /retry/i }).click();
    await expect(page.getByText(/I'd be happy to help/i)).toBeVisible({ timeout: 5000 });
  });

  test('should meet WCAG 2.1 AA contrast requirements', async ({ page }) => {
    // This would use axe-playwright or similar
    const accessibilityScanResults = await page.evaluate(() => {
      // axe-core integration would go here
      return { violations: [] };
    });

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });
});
```

*Code Review Iteration Cycle:*

**Initial Frontend Review:**
```markdown
FRONTEND CODE REVIEW - ChatWidget Component
Reviewer: frontend-code-reviewer agent
Date: 2024-01-20

❌ CRITICAL (1):
1. [Line 247] Missing ARIA live region for dynamic message updates
   - Screen readers won't announce new bot messages
   - WCAG 2.1 AA violation (4.1.3 Status Messages)
   - Fix: Add aria-live="polite" to MessageList container

⚠️ HIGH PRIORITY (2):
1. [Line 236-240] useChatMessages hook lacks error handling
   - Network failures will crash the component
   - No user feedback on API errors
   - Fix: Implement error boundary + error state in hook

2. [Line 255] Input component missing maxLength validation
   - Users can submit very large messages (DoS vector)
   - Backend has 500 char limit but frontend doesn't enforce
   - Fix: Add maxLength prop and character counter

⚠️ MEDIUM PRIORITY (3):
1. [Lines 249-252] MessageList should implement virtual scrolling
   - Performance degrades with 1000+ messages
   - Memory usage grows unbounded
   - Recommendation: Use react-window or react-virtuoso

2. [Line 238] sendMessage not debounced
   - Users can spam messages by rapid clicking
   - Should debounce button clicks (300ms)

3. Missing loading skeleton
   - Initial load shows empty UI briefly
   - Poor UX during first render

✅ STRENGTHS:
- Excellent TypeScript typing throughout
- Proper memoization with useCallback
- Clean component composition
- Keyboard navigation implemented correctly

RECOMMENDATION: Address CRITICAL and HIGH priority issues before merge
```

**Developer Fixes (Round 1):**
```typescript
// FIXED: Added ARIA live region and error handling
export const ChatWidget: React.FC = () => {
  const { messages, sendMessage, isLoading, error } = useChatMessages();
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = useCallback(async () => {
    if (!inputValue.trim() || inputValue.length > 500) return;
    await sendMessage(inputValue);
    setInputValue('');
  }, [inputValue, sendMessage]);

  // FIX: Added error boundary wrapper in parent
  if (error) {
    return <ChatError error={error} onRetry={() => window.location.reload()} />;
  }

  return (
    <div className="chat-widget" role="region" aria-label="Customer service chat">
      <MessageList
        messages={messages}
        aria-live="polite"  // FIXED: CRITICAL issue #1
        aria-atomic="false"
      />
      <ChatInput
        value={inputValue}
        onChange={setInputValue}
        onSubmit={handleSubmit}
        disabled={isLoading}
        maxLength={500}     // FIXED: HIGH priority issue #2
        aria-label="Type your message"
      />
      {inputValue.length > 450 && (
        <CharacterCounter current={inputValue.length} max={500} />
      )}
    </div>
  );
};

// useChatMessages.ts - Added error handling
export function useChatMessages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);  // FIXED: HIGH priority issue #1

  const sendMessage = useCallback(async (text: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: text }),
        signal: AbortSignal.timeout(10000)  // 10s timeout
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();
      setMessages(prev => [...prev, data.userMessage, data.botMessage]);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { messages, sendMessage, isLoading, error };
}
```

**Backend Fixes (Round 1):**
```go
// FIXED: Added rate limiting, timeout, and circuit breaker

import (
    "context"
    "time"
    "github.com/go-redis/redis_rate/v10"
    "github.com/sony/gobreaker"
)

type Service struct {
    llmClient              llm.Client
    llmClientWithBreaker   *gobreaker.CircuitBreaker  // FIXED: Circuit breaker
    sentimentClient        sentiment.Analyzer
    repo                   Repository
    rateLimiter           *redis_rate.Limiter         // FIXED: Rate limiting
}

func NewService(llm llm.Client, sentiment sentiment.Analyzer, repo Repository, rdb *redis.Client) *Service {
    // Circuit breaker configuration
    cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
        Name:        "llm-api",
        MaxRequests: 3,
        Interval:    time.Minute,
        Timeout:     30 * time.Second,
        ReadyToTrip: func(counts gobreaker.Counts) bool {
            failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
            return counts.Requests >= 3 && failureRatio >= 0.6
        },
    })

    return &Service{
        llmClient:            llm,
        llmClientWithBreaker: cb,
        sentimentClient:      sentiment,
        repo:                 repo,
        rateLimiter:         redis_rate.NewLimiter(rdb),
    }
}

func (s *Service) ProcessMessage(ctx context.Context, req MessageRequest) (*MessageResponse, error) {
    // FIXED: Request timeout
    ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
    defer cancel()

    // FIXED: Rate limiting (10 messages per minute per user)
    res, err := s.rateLimiter.Allow(ctx, fmt.Sprintf("user:%s", req.UserID), redis_rate.PerMinute(10))
    if err != nil {
        return nil, err
    }
    if res.Remaining == 0 {
        return nil, ErrRateLimitExceeded
    }

    // Validate input
    if err := req.Validate(); err != nil {
        return nil, ErrInvalidInput
    }

    // Analyze sentiment
    sentimentScore, err := s.sentimentClient.Analyze(ctx, req.Message)
    if err != nil {
        return nil, err
    }

    // Check if escalation needed
    if sentimentScore < -0.7 {
        return s.escalateToHuman(ctx, req)
    }

    // FIXED: LLM call with circuit breaker
    responseInterface, err := s.llmClientWithBreaker.Execute(func() (interface{}, error) {
        return s.llmClient.Chat(ctx, llm.ChatRequest{
            Messages:    s.buildContext(req),
            Temperature: 0.7,
            MaxTokens:   500,
        })
    })

    if err != nil {
        if err == gobreaker.ErrOpenState {
            // Circuit open - use fallback
            return s.getFallbackResponse(ctx, req)
        }
        return nil, err
    }

    response := responseInterface.(*llm.ChatResponse)

    // Store conversation
    if err := s.repo.SaveMessage(ctx, req, response); err != nil {
        return nil, err
    }

    return &MessageResponse{
        Message:            response.Content,
        Sentiment:          sentimentScore,
        RequiresEscalation: false,
    }, nil
}

func (s *Service) getFallbackResponse(ctx context.Context, req MessageRequest) (*MessageResponse, error) {
    // Fallback when LLM is unavailable
    return &MessageResponse{
        Message:            "I'm experiencing technical difficulties. A human agent will assist you shortly.",
        Sentiment:          0,
        RequiresEscalation: true,
    }, nil
}
```

**Re-Review After Fixes:**
```markdown
FRONTEND RE-REVIEW - ChatWidget Component
Reviewer: frontend-code-reviewer agent
Date: 2024-01-21

✅ PREVIOUSLY CRITICAL - NOW RESOLVED:
1. [FIXED] ARIA live region implemented correctly
   - aria-live="polite" added to MessageList
   - aria-atomic="false" for incremental updates
   - Screen reader testing confirms announcements work

✅ PREVIOUSLY HIGH PRIORITY - NOW RESOLVED:
1. [FIXED] Error handling implemented
   - Error boundary in parent component
   - Error state in useChatMessages hook
   - User-friendly error UI with retry option

2. [FIXED] Input validation added
   - maxLength={500} enforced
   - Character counter shown at 450 chars
   - Validates on both client and server

⚠️ REMAINING MEDIUM PRIORITY (2):
1. Virtual scrolling not yet implemented
   - Acceptable for initial release (most conversations < 100 messages)
   - Should address in next sprint for power users

2. Debouncing not implemented
   - Rate limiting on backend mitigates this
   - Client-side debounce would still improve UX

✅ NEW IMPROVEMENTS NOTED:
- Added 10s timeout to fetch requests (prevents hung connections)
- Character counter provides good UX feedback
- Error recovery flow is well-designed

RECOMMENDATION: ✅ APPROVED FOR MERGE
- All critical and high priority issues resolved
- Medium priority items tracked for next iteration
- Code quality has improved significantly

BACKEND RE-REVIEW - Conversation Service
Reviewer: backend-code-reviewer agent
Date: 2024-01-21

✅ ALL HIGH PRIORITY ISSUES RESOLVED:
1. [FIXED] Rate limiting implemented
   - Redis-based rate limiter
   - 10 messages/minute per user
   - Proper error handling for rate limit exceeded

2. [FIXED] Request timeout implemented
   - 10 second context timeout
   - Prevents resource exhaustion

3. [FIXED] Circuit breaker implemented
   - Gobreaker library integration
   - Proper fallback response when circuit open
   - Conservative settings (3 requests, 60% failure ratio)

✅ EXCELLENT IMPROVEMENTS:
- Circuit breaker fallback gracefully escalates to human
- Rate limiter uses Redis (distributed, not just in-memory)
- Timeout applied correctly with context.WithTimeout

💡 MINOR SUGGESTIONS (Not blocking):
1. Consider adding response caching for common queries
   - Could reduce LLM API costs by 30-40%
   - Redis already available for cache backend

2. Add distributed tracing (OpenTelemetry)
   - Would help debug cross-service latency
   - Useful for production observability

3. Circuit breaker settings could be configurable
   - Current settings hardcoded
   - Consider moving to config file for easier tuning

RECOMMENDATION: ✅ APPROVED FOR MERGE
- All critical issues addressed professionally
- Production-ready with good resilience patterns
- Minor suggestions can be addressed in future PRs

SECURITY REVIEW: ✅ PASSED
- Rate limiting prevents abuse
- Input validation on size and content
- No new security concerns introduced
```

**Final Summary:**
```
CODE REVIEW COMPLETE - READY FOR VALIDATION PHASE

Frontend Changes:
- 3 files modified
- 1 critical issue fixed (accessibility)
- 2 high priority issues fixed (error handling, validation)
- Test coverage increased to 89%

Backend Changes:
- 2 files modified
- 3 high priority issues fixed (rate limit, timeout, circuit breaker)
- Added resilience patterns
- Test coverage: 92%

Time to Resolution:
- Initial review: Jan 20, 10:00 AM
- Fixes completed: Jan 21, 2:00 PM
- Re-review approved: Jan 21, 4:00 PM
- Total iteration time: ~1.5 days

Ready for /jpspec:validate phase
```

---

### Step 5: Validation and Quality Assurance

**Command:**
```bash
/jpspec:validate AI customer service chatbot
```

**What happens:**

**Phase 1 (Parallel):**
- **Quality-guardian agent**: Runs comprehensive QA testing (functional, integration, performance, accessibility)
- **Secure-by-design-engineer agent**: Conducts security assessment (code review, dependency scan, penetration testing)

**Phase 2 (Sequential):**
- **Tech-writer agent**: Creates comprehensive documentation (API docs, user guides, runbooks)

**Phase 3 (Final Gate):**
- **Release-manager agent**: Assesses release readiness and **requests human approval** before production

**Deliverables:**
- QA test report with quality metrics
- Security assessment report with vulnerability findings
- Complete documentation package
- Release readiness assessment
- Human approval checkpoint

**Output includes:**

*QA Test Report:*

```markdown
QUALITY ASSURANCE TEST REPORT
Tester: quality-guardian agent
Date: 2024-01-23
Test Environment: Staging (production-like)
Test Duration: 48 hours

═══════════════════════════════════════════════════════════════

EXECUTIVE SUMMARY:
Overall Status: ✅ PASSED (147/147 functional tests, all NFRs met)
Quality Score: 94/100 (Excellent)
Production Readiness: ✅ APPROVED

═══════════════════════════════════════════════════════════════

1. FUNCTIONAL TESTING (147/147 PASSED - 100%)

Conversational Flow:
✅ User can initiate conversation                      [TC-001]
✅ Bot responds within 2s for simple queries           [TC-002]
✅ Multi-turn conversations maintain context           [TC-003]
✅ Conversation history persists across sessions       [TC-004]
✅ User can end conversation gracefully                [TC-005]

Sentiment Analysis & Escalation:
✅ Positive sentiment (>0.5) handled normally          [TC-010]
✅ Neutral sentiment (0 to 0.5) handled normally       [TC-011]
✅ Negative sentiment (-0.7 to 0) monitored            [TC-012]
✅ Very negative sentiment (<-0.7) triggers escalation [TC-013]
   Test case: "I'm extremely frustrated and angry!"
   Result: Escalation triggered immediately, human agent notified

Multi-Language Support:
✅ English (EN): Tested with 50 queries                [TC-020-024]
✅ Spanish (ES): Tested with 25 queries                [TC-025-029]
✅ French (FR): Tested with 25 queries                 [TC-030-034]
✅ German (DE): Tested with 25 queries                 [TC-035-039]
   Language auto-detection accuracy: 98.7%

Knowledge Base Integration:
✅ Returns relevant results for product questions      [TC-040]
✅ Handles "no results found" gracefully               [TC-041]
✅ Vector similarity search works correctly            [TC-042]
   Average relevance score: 0.87/1.0 (Good)

Error Handling:
✅ Invalid input handled with user-friendly message    [TC-050]
✅ LLM API timeout triggers fallback response          [TC-051]
✅ Network errors show retry option                    [TC-052]
✅ Rate limit exceeded shows clear message             [TC-053]

Edge Cases:
✅ Very long messages (500 chars) processed correctly  [TC-060]
✅ Messages with special characters/emojis work        [TC-061]
✅ Rapid message submission handled (rate limiting)    [TC-062]
✅ Concurrent conversations from same user work        [TC-063]

═══════════════════════════════════════════════════════════════

2. PERFORMANCE TESTING ✅ ALL TARGETS MET

Load Testing (Simulated 1,000 concurrent users):
┌─────────────────┬────────┬────────┬──────────┐
│ Metric          │ Result │ Target │ Status   │
├─────────────────┼────────┼────────┼──────────┤
│ p50 Latency     │  89ms  │ <100ms │ ✅ PASS  │
│ p95 Latency     │ 187ms  │ <200ms │ ✅ PASS  │
│ p99 Latency     │ 312ms  │ <500ms │ ✅ PASS  │
│ Max Latency     │ 487ms  │ <1s    │ ✅ PASS  │
│ Throughput      │ 1,247  │ 1,000  │ ✅ PASS  │
│                 │ req/s  │ req/s  │          │
│ Error Rate      │ 0.03%  │ <0.1%  │ ✅ PASS  │
│ CPU Usage       │  67%   │ <80%   │ ✅ PASS  │
│ Memory Usage    │ 1.2GB  │ <2GB   │ ✅ PASS  │
└─────────────────┴────────┴────────┴──────────┘

Stress Testing (Simulated 5,000 concurrent users):
- System remained stable
- No crashes or memory leaks observed
- Graceful degradation when approaching limits
- HPA scaled pods from 3 → 12 → 20 automatically
- Response time increased to p95: 450ms (acceptable)

Endurance Testing (24-hour soak test):
✅ No memory leaks detected
✅ Connection pool stable (no exhaustion)
✅ Database query performance consistent
✅ LLM API circuit breaker triggered 3 times (recovered automatically)

Performance Bottlenecks Identified:
⚠️ LLM API calls: 150-200ms average (external dependency)
   - Mitigation: Response caching for common queries (roadmap)
✅ Database queries: <10ms average (well-optimized)
✅ Sentiment analysis: 45ms average (acceptable)

═══════════════════════════════════════════════════════════════

3. ACCESSIBILITY TESTING ✅ WCAG 2.1 AA COMPLIANT

Automated Testing (axe-core):
✅ 0 critical violations
✅ 0 serious violations
⚠️ 2 moderate issues (informational only):
   - Alt text could be more descriptive on logo
   - Heading hierarchy skip from h1 to h3 (not impactful)

Manual Testing Results:

Keyboard Navigation:
✅ All interactive elements reachable via Tab
✅ Enter/Space activate buttons correctly
✅ Escape closes dialogs
✅ Arrow keys navigate message list
✅ Focus indicators clearly visible (3px blue outline)
✅ No keyboard traps detected

Screen Reader Testing (NVDA, JAWS, VoiceOver):
✅ NVDA (Windows): Full functionality, announcements correct
✅ JAWS (Windows): Full functionality, ARIA live regions work
✅ VoiceOver (macOS): Full functionality, good navigation
   Test scenario: Complete conversation without mouse
   Result: 100% task completion by blind tester

Visual Requirements:
✅ Color contrast ratios meet 4.5:1 minimum
   - Text: 7.2:1 (Excellent)
   - Interactive elements: 5.8:1 (Good)
✅ Text resizable to 200% without loss of function
✅ No content relies solely on color
✅ Focus indicators have 3:1 contrast ratio

Mobile Accessibility:
✅ Touch targets ≥44x44 CSS pixels
✅ Pinch-to-zoom enabled
✅ Orientation changes supported (portrait/landscape)

Accessibility Score: 98/100 (Excellent)

═══════════════════════════════════════════════════════════════

4. CROSS-BROWSER/PLATFORM COMPATIBILITY ✅ PASSED

Desktop Browsers:
✅ Chrome 120 (Windows 11, macOS Sonoma)
✅ Firefox 121 (Windows 11, macOS Sonoma)
✅ Safari 17 (macOS Sonoma)
✅ Edge 120 (Windows 11)

Mobile Browsers:
✅ Safari iOS 17 (iPhone 15 Pro)
✅ Chrome Android 120 (Pixel 8)
✅ Samsung Internet 23 (Galaxy S23)

Responsive Design Testing:
✅ 320px (iPhone SE): Functional, no horizontal scroll
✅ 768px (iPad): Optimal layout
✅ 1920px (Desktop): Excellent layout
✅ 3840px (4K): Scales appropriately

═══════════════════════════════════════════════════════════════

5. INTEGRATION TESTING ✅ PASSED

Frontend ↔ Backend:
✅ WebSocket connection stable
✅ API authentication working
✅ Error responses handled correctly
✅ Loading states synchronized

Backend ↔ LLM API:
✅ GPT-4 integration working
✅ Circuit breaker triggers correctly after 3 failures
✅ Fallback to Claude works when GPT-4 unavailable
✅ Streaming responses handled correctly

Backend ↔ Sentiment Model:
✅ Sentiment scores accurate (validated against 1,000 samples)
✅ Model inference <50ms
✅ Batch processing works for analytics

Backend ↔ Knowledge Base:
✅ Vector similarity search returns relevant docs
✅ Query performance <100ms
✅ Handles empty results gracefully

═══════════════════════════════════════════════════════════════

6. SECURITY TESTING (Collaboration with Security Team)

Authentication & Authorization:
✅ JWT tokens expire correctly (15min)
✅ Refresh token rotation works
✅ Cannot access other users' conversations
✅ Admin endpoints require proper roles

Input Validation:
✅ XSS attempts blocked (tested 25 payloads)
✅ SQL injection prevented (parameterized queries)
✅ Path traversal attempts blocked
✅ File upload validation working (if applicable)

Rate Limiting:
✅ 10 messages/minute limit enforced
✅ IP-based rate limiting for anonymous users
✅ Burst protection working

═══════════════════════════════════════════════════════════════

7. NON-FUNCTIONAL REQUIREMENTS

Scalability:
✅ Horizontal scaling tested (3 → 20 pods)
✅ Load balancer distributes traffic evenly
✅ Stateless design allows easy scaling
✅ Database connection pooling prevents exhaustion

Reliability:
✅ Uptime during test period: 99.97%
✅ Zero data loss incidents
✅ Automatic pod recovery after crashes
✅ Circuit breaker prevents cascade failures

Maintainability:
✅ Code coverage: 89% (Frontend), 92% (Backend)
✅ No critical code smells (SonarQube scan)
✅ Technical debt ratio: 0.8% (Excellent)
✅ Documentation completeness: 95%

Monitoring & Observability:
✅ All critical metrics instrumented
✅ Logs structured and queryable
✅ Distributed tracing shows full request path
✅ Alerts fire correctly for SLO violations

═══════════════════════════════════════════════════════════════

8. RISK ASSESSMENT

Risk Matrix:
┌─────────────────────────┬───────────┬────────┬──────────┐
│ Risk                    │ Likelihood│ Impact │ Severity │
├─────────────────────────┼───────────┼────────┼──────────┤
│ LLM API outage          │ Low (5%)  │ High   │ MEDIUM   │
│ High traffic spike      │ Med (20%) │ Med    │ MEDIUM   │
│ Database failure        │ Low (2%)  │ High   │ LOW      │
│ Security breach         │ Very Low  │ High   │ LOW      │
│ Data corruption         │ Very Low  │ High   │ LOW      │
└─────────────────────────┴───────────┴────────┴──────────┘

Mitigation Strategy:
✅ LLM API outage: Circuit breaker + fallback responses
✅ Traffic spike: HPA configured, tested to 5,000 users
✅ Database failure: Automated backups every 6 hours, tested restores
✅ Security breach: Defense in depth, regular security scans
✅ Data corruption: Database transactions + audit logging

Overall Risk: ✅ LOW (all risks have effective mitigations)

═══════════════════════════════════════════════════════════════

9. DEFECTS IDENTIFIED

During testing, 12 defects found and fixed:
✅ DEF-001: Character counter not showing (FIXED - Critical)
✅ DEF-002: Focus lost after sending message (FIXED - High)
✅ DEF-003: Screen reader not announcing bot messages (FIXED - High)
✅ DEF-004: Error retry button not working (FIXED - Medium)
... (all 12 defects resolved and re-tested)

Open Issues: 0 Critical, 0 High, 0 Medium
Post-launch monitoring recommended for 2 minor UX improvements

═══════════════════════════════════════════════════════════════

10. FINAL RECOMMENDATION

Quality Gate Status:
✅ Functional tests: 100% pass rate (147/147)
✅ Performance: All SLOs met
✅ Accessibility: WCAG 2.1 AA compliant
✅ Security: All high/critical issues resolved
✅ Integration: All systems working correctly
✅ Risk: LOW with effective mitigations

RECOMMENDATION: ✅ APPROVED FOR PRODUCTION RELEASE

Confidence Level: HIGH (94/100)
Suggested monitoring focus areas:
- LLM API latency and circuit breaker triggers
- Sentiment analysis accuracy in production
- User escalation rates
- p95/p99 latency under real traffic

Next Steps:
1. Proceed to release management approval
2. Schedule deployment for low-traffic window
3. Enable progressive rollout (canary → 100%)
4. Monitor closely for first 48 hours
```

*Security Assessment:*

**Phase 1: Automated Security Scans**

```bash
# Dependency vulnerability scanning
$ npm audit
found 3 vulnerabilities (2 moderate, 1 high)

$ trivy fs --security-checks vuln,config .
Total: 5 (HIGH: 1, MEDIUM: 2, LOW: 2)
```

**Detailed Vulnerability Report:**

```markdown
SECURITY ASSESSMENT REPORT
Assessor: secure-by-design-engineer agent
Date: 2024-01-22
Scope: AI Customer Service Chatbot (Frontend, Backend, ML, Infrastructure)

═══════════════════════════════════════════════════════════════

EXECUTIVE SUMMARY:
- Total Findings: 8
- Critical: 0 ✅
- High: 1 ⚠️
- Medium: 4 ⚠️
- Low: 3 ℹ️
- Status: CONDITIONAL APPROVAL (fix High before production)

═══════════════════════════════════════════════════════════════

HIGH SEVERITY (1) - MUST FIX BEFORE PRODUCTION

[H-001] Dependency: axios SSRF Vulnerability
├─ Package: axios@0.27.2
├─ CVE: CVE-2023-45857
├─ CVSS: 7.5 (High)
├─ Description: Server-Side Request Forgery in axios HTTP client
│  - Attacker can manipulate HTTP redirects
│  - Potential for internal network scanning
│  - Affects backend LLM API client
├─ Affected Files:
│  - internal/llm/openai_client.go (uses axios via proxy)
│  - ml_services/sentiment_analyzer.py (HTTP requests)
├─ Exploit Scenario:
│  1. Attacker crafts malicious LLM response with redirect
│  2. Axios follows redirect to internal service (e.g., metadata endpoint)
│  3. Sensitive data leaked in subsequent request
├─ Remediation:
│  ✓ Update axios to 1.6.2 or later
│  ✓ Add maxRedirects: 0 to axios config
│  ✓ Implement allowlist for redirect domains
├─ Fix:
   ```bash
   npm install axios@1.6.2
   pip install httpx==0.25.2  # Python alternative
   ```
├─ Verification:
   npm audit --omit=dev  # Should show 0 high vulnerabilities

═══════════════════════════════════════════════════════════════

MEDIUM SEVERITY (4) - FIX BEFORE PRODUCTION RECOMMENDED

[M-001] Dependency: react-dom Prototype Pollution
├─ Package: react-dom@18.2.0
├─ CVE: CVE-2024-21849
├─ CVSS: 5.3 (Medium)
├─ Description: Prototype pollution via server components
│  - Theoretical attack, difficult to exploit in production
│  - Requires specific SSR configuration
├─ Affected Files: src/index.tsx (client-side only, low risk)
├─ Remediation:
   ```bash
   npm install react-dom@18.2.1
   ```

[M-002] Missing Security Headers
├─ Severity: Medium
├─ Description: API Gateway missing security headers
│  - No X-Frame-Options (clickjacking risk)
│  - No Content-Security-Policy (XSS defense)
│  - No X-Content-Type-Options (MIME sniffing)
├─ Affected: API Gateway (Kong/Traefik)
├─ Remediation:
   ```yaml
   # kong.yml or traefik config
   headers:
     customResponseHeaders:
       X-Frame-Options: "DENY"
       X-Content-Type-Options: "nosniff"
       Content-Security-Policy: "default-src 'self'; script-src 'self' 'unsafe-inline'"
       Strict-Transport-Security: "max-age=31536000; includeSubDomains"
       Permissions-Policy: "geolocation=(), microphone=(), camera=()"
   ```

[M-003] Insufficient Logging of Security Events
├─ Severity: Medium
├─ Description: Security-relevant events not logged
│  - Authentication failures not logged
│  - Rate limit violations not logged
│  - Escalations to human not tracked
├─ Impact: Difficult to detect attacks or abuse
├─ Remediation:
   ```go
   // Add security event logging
   func (s *Service) ProcessMessage(ctx context.Context, req MessageRequest) (*MessageResponse, error) {
       // ... existing code ...

       if res.Remaining == 0 {
           s.securityLogger.Warn("Rate limit exceeded",
               "user_id", req.UserID,
               "ip", getClientIP(ctx),
               "timestamp", time.Now())
           return nil, ErrRateLimitExceeded
       }

       if sentimentScore < -0.7 {
           s.securityLogger.Info("Escalation triggered",
               "user_id", req.UserID,
               "sentiment_score", sentimentScore,
               "message_hash", hashMessage(req.Message))
           return s.escalateToHuman(ctx, req)
       }
   }
   ```

[M-004] ML Model Supply Chain Risk
├─ Severity: Medium
├─ Description: ML model downloaded from Hugging Face without verification
│  - No checksum validation
│  - No model signature verification
│  - Potential for model poisoning attack
├─ Affected: ml_services/sentiment_analyzer.py
├─ Remediation:
   ```python
   # Add model verification
   import hashlib

   class SentimentAnalyzer:
       EXPECTED_MODEL_HASH = "a3f9bc8e72d1f9a8b2c3d4e5f6a7b8c9"

       def __init__(self, model_name: str):
           self.model = AutoModelForSequenceClassification.from_pretrained(
               model_name,
               revision="main",  # Pin to specific version
               force_download=False,
               resume_download=True
           )

           # Verify model integrity
           model_hash = self._compute_model_hash()
           if model_hash != self.EXPECTED_MODEL_HASH:
               raise SecurityError("Model hash mismatch - possible tampering")

       def _compute_model_hash(self) -> str:
           # Hash model weights for integrity check
           hasher = hashlib.sha256()
           for param in self.model.parameters():
               hasher.update(param.data.cpu().numpy().tobytes())
           return hasher.hexdigest()[:40]
   ```

═══════════════════════════════════════════════════════════════

LOW SEVERITY (3) - INFORMATIONAL

[L-001] Verbose Error Messages in Production
├─ Severity: Low
├─ Description: Stack traces exposed in API error responses
│  - Could reveal internal structure to attackers
│  - Seen in /api/chat endpoint error responses
├─ Remediation: Use generic error messages in production
   ```go
   if env == "production" {
       return &ErrorResponse{Message: "Internal server error"}
   } else {
       return &ErrorResponse{Message: err.Error(), Stack: debug.Stack()}
   }
   ```

[L-002] Missing Rate Limiting on Static Assets
├─ Severity: Low
├─ Description: Frontend static assets not rate-limited
│  - Potential for bandwidth exhaustion
│  - Low risk (CDN in front)
├─ Remediation: Add Cloudflare rate limiting or similar

[L-003] Database Connection String in Logs
├─ Severity: Low
├─ Description: Connection string logged during startup
│  - Contains sensitive connection details
│  - Visible in startup logs
├─ Remediation: Redact connection strings in logs
   ```go
   logger.Info("Database connected", "host", redact(dbConfig.Host))
   ```

═══════════════════════════════════════════════════════════════

COMPLIANCE ASSESSMENT:

✅ GDPR Compliance:
- Data minimization: PASS (only stores necessary chat data)
- Right to deletion: IMPLEMENTED (user data deletion API)
- Data encryption: PASS (TLS 1.3, encryption at rest)
- Consent management: PENDING (needs cookie consent banner)

✅ SOC 2 Requirements:
- Access controls: PASS (RBAC configured)
- Audit logging: PARTIAL (needs security event logging - see M-003)
- Data encryption: PASS
- Incident response: PASS (runbooks documented)

⚠️ PCI DSS: N/A (no payment card data)
⚠️ HIPAA: N/A (no PHI data)

═══════════════════════════════════════════════════════════════

PENETRATION TESTING SUMMARY:

Manual security testing performed:
✅ Authentication bypass attempts: FAILED (no vulnerabilities)
✅ SQL injection testing: PASSED (parameterized queries used)
✅ XSS attacks: PASSED (React escaping + CSP once headers added)
✅ CSRF testing: PASSED (SameSite cookies, token validation)
✅ Authorization escalation: PASSED (proper permission checks)

═══════════════════════════════════════════════════════════════

REMEDIATION PLAN:

Immediate (Block Production):
1. [H-001] Update axios to 1.6.2                     [Priority: P0]
2. Add redirect controls to HTTP clients              [Priority: P0]

Before Production (Recommended):
3. [M-001] Update react-dom to 18.2.1                [Priority: P1]
4. [M-002] Add security headers to API Gateway        [Priority: P1]
5. [M-003] Implement security event logging           [Priority: P1]
6. [M-004] Add ML model integrity verification        [Priority: P1]

Post-Production (Nice to Have):
7. [L-001] Generic error messages in production       [Priority: P2]
8. [L-002] Rate limiting on static assets             [Priority: P3]
9. [L-003] Redact sensitive data in logs              [Priority: P2]

Estimated Remediation Time: 4-6 hours

═══════════════════════════════════════════════════════════════

FINAL RECOMMENDATION: ⚠️ CONDITIONAL APPROVAL

✅ Code security: STRONG (good practices throughout)
⚠️ Dependencies: FIX HIGH severity axios vulnerability
⚠️ Infrastructure: ADD security headers
✅ Compliance: COMPLIANT (with minor enhancements needed)

APPROVAL STATUS: Fix H-001 (axios SSRF) before production deployment.
After remediation, re-scan and approve for production release.
```

**Post-Remediation Security Scan:**

```bash
# After fixing high priority issues
$ npm install axios@1.6.2 react-dom@18.2.1
$ npm audit
found 0 vulnerabilities ✅

$ trivy fs --security-checks vuln,config --severity HIGH,CRITICAL .
Total: 0 (HIGH: 0, CRITICAL: 0) ✅

# Security headers verification
$ curl -I https://chatbot-api.example.com/health
HTTP/2 200
x-frame-options: DENY
x-content-type-options: nosniff
content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline'
strict-transport-security: max-age=31536000; includeSubDomains

SECURITY RE-ASSESSMENT: ✅ APPROVED FOR PRODUCTION
All high and medium priority vulnerabilities resolved.
Production deployment authorized.
```

*Documentation Generation Examples:*

**API Documentation (Generated by tech-writer agent):**

````markdown
# Chat API Reference

## POST /api/v1/chat/messages

Send a message to the AI chatbot and receive a response.

### Authentication
Requires Bearer token in Authorization header.

### Request

```http
POST /api/v1/chat/messages
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "Hello, I need help with my order",
  "conversation_id": "conv_abc123", // Optional, for continuing conversation
  "user_id": "user_xyz789",
  "metadata": {
    "source": "web",
    "language": "en"
  }
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | User message (max 500 characters) |
| `conversation_id` | string | No | ID of existing conversation |
| `user_id` | string | Yes | Authenticated user ID |
| `metadata` | object | No | Additional context |

### Response (200 OK)

```json
{
  "message_id": "msg_def456",
  "conversation_id": "conv_abc123",
  "response": {
    "content": "I'd be happy to help with your order! Could you please provide your order number?",
    "sentiment_score": 0.85,
    "requires_escalation": false
  },
  "metadata": {
    "processing_time_ms": 187,
    "model": "gpt-4",
    "confidence": 0.92
  },
  "timestamp": "2024-01-24T10:30:45Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `message_id` | string | Unique message identifier |
| `response.content` | string | Chatbot response text |
| `response.sentiment_score` | number | User sentiment (-1 to 1) |
| `response.requires_escalation` | boolean | Whether human agent needed |

### Error Responses

**400 Bad Request**
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Message exceeds maximum length of 500 characters",
    "details": {
      "field": "message",
      "actual_length": 612,
      "max_length": 500
    }
  }
}
```

**429 Too Many Requests**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit of 10 messages per minute exceeded",
    "retry_after": 45
  }
}
```

**503 Service Unavailable**
```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "LLM service temporarily unavailable. Please try again shortly.",
    "fallback_available": true
  }
}
```

### Examples

**Simple Message:**
```bash
curl -X POST https://api.chatbot.example.com/v1/chat/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your business hours?",
    "user_id": "user_123"
  }'
```

**Continue Conversation:**
```bash
curl -X POST https://api.chatbot.example.com/v1/chat/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Order number 12345",
    "conversation_id": "conv_abc123",
    "user_id": "user_123"
  }'
```

### Rate Limits
- 10 messages per minute per user
- 1,000 requests per hour per API key
- Burst allowance: 20 messages

### Best Practices
1. Always include `conversation_id` for multi-turn conversations
2. Handle rate limit errors gracefully with exponential backoff
3. Implement timeout of 10 seconds for API calls
4. Monitor `requires_escalation` field and route to human agents accordingly
````

**User Guide Excerpt:**

````markdown
# Getting Started with AI Customer Service

## For End Users

### Starting a Conversation

1. Click the chat widget in the bottom-right corner of the page
2. Type your question or issue in the message box
3. Press Enter or click Send

The AI assistant will respond within 2 seconds.

### Tips for Best Results

✅ **Be specific**: "I need help with order #12345" is better than "I have a problem"
✅ **One question at a time**: Let the bot answer before asking a follow-up
✅ **Provide context**: Mention relevant details (order number, account email, etc.)

### When You'll Talk to a Human

The bot automatically connects you to a human agent when:
- Your question is complex and requires human judgment
- You express frustration (we detect this and escalate)
- The bot can't find an answer in the knowledge base

You'll see a clear message: "Connecting you to a human agent..."

### Privacy & Security

- Conversations are encrypted end-to-end
- We only store messages for 30 days
- You can request deletion of your data anytime
- No personal information is shared with third parties
````

**Operational Runbook:**

````markdown
# Runbook: High Error Rate Alert

## Alert Definition
Triggers when error rate > 1% for 5 consecutive minutes

## Severity
🔴 **HIGH** - Immediate response required

## Symptoms
- Users seeing "Service Unavailable" errors
- Increased complaints about bot not responding
- Grafana dashboard shows spike in 5xx errors

## Investigation Steps

### 1. Check System Health
```bash
# Check pod status
kubectl get pods -n chatbot

# Expected: All pods Running/Ready
# If CrashLoopBackOff, proceed to step 3
```

### 2. Check Recent Deployments
```bash
# List recent deployments
kubectl rollout history deployment/chatbot-api -n chatbot

# If deployment within last hour, likely cause
```

### 3. Check Logs
```bash
# View recent errors
kubectl logs -n chatbot -l app=chatbot --tail=100 | grep ERROR

# Common error patterns:
# - "connection refused" → Database connectivity
# - "timeout" → LLM API latency
# - "rate limit exceeded" → Quota issues
```

### 4. Check Dependencies
```bash
# Check LLM API status
curl https://status.openai.com/api/v2/status.json

# Check database connectivity
kubectl exec -it chatbot-api-xxx -n chatbot -- \
  psql -h $DB_HOST -U $DB_USER -c "SELECT 1;"

# Check Redis
kubectl exec -it chatbot-api-xxx -n chatbot -- \
  redis-cli -h redis-service ping
# Expected: PONG
```

### 5. Check Metrics
- Navigate to Grafana: https://grafana.company.com/d/chatbot
- Review:
  - Request rate (sudden spike?)
  - LLM API latency (> 5s?)
  - Circuit breaker state (open?)
  - Memory/CPU usage (approaching limits?)

## Common Causes & Fixes

### Cause 1: LLM API Degradation
**Symptoms**: High latency, circuit breaker open
**Fix**:
```bash
# Check circuit breaker status
kubectl exec -it chatbot-api-xxx -n chatbot -- \
  curl localhost:8080/debug/circuit-breaker

# If open, wait for recovery (30s timeout)
# Or manually scale to trigger fallback mode
kubectl scale deployment chatbot-api --replicas=0 -n chatbot
sleep 10
kubectl scale deployment chatbot-api --replicas=3 -n chatbot
```

### Cause 2: Database Connection Exhaustion
**Symptoms**: "too many connections" in logs
**Fix**:
```bash
# Check active connections
kubectl exec -it postgres-0 -n chatbot -- \
  psql -c "SELECT count(*) FROM pg_stat_activity;"

# If > 90, restart problematic pods
kubectl delete pod chatbot-api-xxx -n chatbot
```

### Cause 3: Memory Leak
**Symptoms**: OOMKilled pods, gradual memory increase
**Fix**:
```bash
# Immediate: Restart pods
kubectl rollout restart deployment/chatbot-api -n chatbot

# Long-term: Scale horizontally until fix deployed
kubectl scale deployment chatbot-api --replicas=6 -n chatbot
```

### Cause 4: Bad Deployment
**Symptoms**: Errors started after recent deployment
**Fix**:
```bash
# Rollback to previous version
kubectl rollout undo deployment/chatbot-api -n chatbot

# Verify rollback successful
kubectl rollout status deployment/chatbot-api -n chatbot
```

## Resolution Verification

After applying fix, verify:
```bash
# 1. Check error rate dropped
# Visit Grafana dashboard, confirm < 0.1% error rate

# 2. Test end-to-end
curl -X POST https://api.chatbot.example.com/v1/chat/messages \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_id": "test"}'

# 3. Verify logs clean
kubectl logs -n chatbot -l app=chatbot --tail=50 | grep ERROR
# Expected: No new errors
```

## Escalation

If unresolved after 15 minutes:
1. Page on-call SRE via PagerDuty
2. Notify #incidents Slack channel
3. Consider enabling maintenance mode

## Post-Incident

After resolution:
1. Update incident log in Confluence
2. Schedule post-mortem within 48 hours
3. Create JIRA tickets for root cause fixes
4. Update this runbook if new insights gained
````

*Release Management with Human Approval:*

```markdown
RELEASE READINESS ASSESSMENT
Release Manager: release-manager agent
Date: 2024-01-24
Release Version: v1.2.0 - AI Customer Service Chatbot

═══════════════════════════════════════════════════════════════

PRE-RELEASE VALIDATION CHECKLIST

Quality Gates:
✅ Functional tests: 147/147 passed (100%)
✅ Code coverage: 89% frontend, 92% backend (target: 80%)
✅ Security scan: ✅ PASSED (all high/critical issues resolved)
✅ Performance benchmarks: ✅ ALL SLOs MET
   - p95 latency: 187ms (target: <200ms)
   - Throughput: 1,247 req/s (target: 1,000 req/s)
   - Error rate: 0.03% (target: <0.1%)
✅ Accessibility: ✅ WCAG 2.1 AA COMPLIANT
✅ Documentation: ✅ COMPLETE (API docs, user guides, runbooks)
✅ Monitoring: ✅ CONFIGURED (metrics, logs, traces, alerts)
✅ Runbooks: ✅ VALIDATED (tested with on-call team)

Code Review:
✅ All critical issues resolved
✅ All high priority issues resolved
✅ 2 medium priority items deferred to v1.3.0 (tracked in backlog)
✅ Technical debt: 0.8% (Excellent)

Dependencies:
✅ All production dependencies up to date
✅ No known CVEs in dependency tree
✅ SBOM generated and stored

═══════════════════════════════════════════════════════════════

RELEASE PLANNING

Release Type: **MINOR** (v1.1.0 → v1.2.0)
- New feature: AI chatbot with sentiment analysis
- No breaking changes
- Backward compatible API

Deployment Strategy: **PROGRESSIVE CANARY**
- Phase 1: 10% of traffic (500 users) - 30 min soak
- Phase 2: 50% of traffic (2,500 users) - 1 hour soak
- Phase 3: 100% of traffic - full rollout

Target Deployment Window:
- Date: Tuesday, January 25, 2024
- Time: 10:00 AM PST (low traffic period)
- Duration: ~2 hours (including canary phases)
- Rollback window: Available for 24 hours

Stakeholders:
- Engineering Lead: @alice (approver)
- Product Manager: @bob (informed)
- Customer Support: @carol (informed, prepare for escalations)
- SRE On-Call: @dave (monitoring)

═══════════════════════════════════════════════════════════════

RISK ASSESSMENT

Deployment Risks:
┌───────────────────────────┬────────┬────────┬──────────┬──────────────┐
│ Risk                      │ Prob.  │ Impact │ Severity │ Mitigation   │
├───────────────────────────┼────────┼────────┼──────────┼──────────────┤
│ LLM API quota exceeded    │ Low    │ High   │ MEDIUM   │ Rate limits  │
│                           │ (10%)  │        │          │ + fallback   │
├───────────────────────────┼────────┼────────┼──────────┼──────────────┤
│ Sentiment model accuracy  │ Med    │ Med    │ MEDIUM   │ Human review │
│                           │ (25%)  │        │          │ for edge     │
│                           │        │        │          │ cases        │
├───────────────────────────┼────────┼────────┼──────────┼──────────────┤
│ High traffic spike        │ Med    │ Low    │ LOW      │ HPA tested   │
│                           │ (30%)  │        │          │ to 5K users  │
├───────────────────────────┼────────┼────────┼──────────┼──────────────┤
│ Database performance      │ Low    │ Med    │ LOW      │ Load tested  │
│                           │ (5%)   │        │          │ + monitoring │
├───────────────────────────┼────────┼────────┼──────────┼──────────────┤
│ Security incident         │ V.Low  │ High   │ LOW      │ Pen tested,  │
│                           │ (2%)   │        │          │ monitoring   │
└───────────────────────────┴────────┴────────┴──────────┴──────────────┘

Overall Risk Level: ✅ **LOW-MEDIUM**

User Impact Assessment:
- Affected Users: All users (5,000 daily active users)
- Impact Type: NEW FEATURE (additive, no disruption to existing flows)
- Fallback: If issues detected, bot disabled, users route to existing support
- Communication: In-app announcement + email to power users

Rollback Plan:
✅ Automated rollback configured
✅ Rollback tested in staging (successful in 2 minutes)
✅ Database migrations backward compatible
✅ Feature flags allow instant disable without redeployment

═══════════════════════════════════════════════════════════════

DEPLOYMENT CHECKLIST

Pre-Deployment:
✅ Merge release branch to main
✅ Tag release: v1.2.0
✅ Generate release notes
✅ Notify stakeholders 24h before
✅ Verify rollback plan tested
✅ On-call engineer confirmed available
✅ Customer support briefed on new feature
✅ Monitoring dashboards reviewed
✅ Alert thresholds configured

During Deployment:
⏹️ Start canary deployment (10%)
⏹️ Monitor metrics for 30 minutes
⏹️ Check error rates, latency, user feedback
⏹️ If healthy, proceed to 50%
⏹️ Monitor for 1 hour
⏹️ If healthy, proceed to 100%
⏹️ Post deployment verification

Post-Deployment:
⏹️ Monitor for 4 hours (extended monitoring)
⏹️ Review customer feedback channels
⏹️ Check error budget consumption
⏹️ Update status page
⏹️ Send deployment completion notification

═══════════════════════════════════════════════════════════════

MONITORING PLAN

Key Metrics to Watch:
1. **Error Rate**: Must stay < 0.1%
   - Alert if > 0.5% for 5 minutes

2. **Latency**: p95 must stay < 200ms
   - Alert if > 300ms for 10 minutes

3. **LLM API Success Rate**: Must stay > 99%
   - Alert if circuit breaker opens

4. **Sentiment Analysis Accuracy**: Monitor escalation rate
   - Expected: 5-10% of conversations escalate
   - Alert if > 20% (over-escalating) or < 2% (under-escalating)

5. **User Engagement**: Monitor adoption
   - Target: 30% of users try chatbot in first week

Dashboards:
- Real-time: https://grafana.company.com/d/chatbot-realtime
- Business metrics: https://grafana.company.com/d/chatbot-business

═══════════════════════════════════════════════════════════════

COMMUNICATION PLAN

**T-24 hours**: Email to internal stakeholders
Subject: AI Chatbot v1.2.0 Deployment - Tuesday 10am PST

**T-1 hour**: Slack announcement in #engineering
"Starting v1.2.0 deployment in 1 hour. Canary rollout, monitoring closely."

**T+0 (during deployment)**: Status updates every 30 min in #incidents
"Canary at 10% - all metrics green"
"Canary at 50% - p95 latency 192ms, error rate 0.02%"
"Rollout complete - monitoring extended for 4 hours"

**T+4 hours**: Final deployment status
Subject: v1.2.0 Deployment Complete - AI Chatbot Live

═══════════════════════════════════════════════════════════════

🚦 GO / NO-GO DECISION

Technical Readiness: ✅ GO
- All quality gates passed
- All tests passing
- Security approved
- Performance validated

Operational Readiness: ✅ GO
- Monitoring configured
- Runbooks tested
- On-call coverage confirmed
- Rollback plan validated

Business Readiness: ✅ GO
- Stakeholders informed
- Customer support trained
- Documentation published
- Communication plan ready

RECOMMENDATION: ✅ **GO FOR PRODUCTION RELEASE**

═══════════════════════════════════════════════════════════════

⏸️  HUMAN APPROVAL REQUIRED

Release Manager Assessment:
- Quality Score: 94/100 (Excellent)
- Risk Level: LOW-MEDIUM
- Confidence: HIGH

This release introduces AI-powered customer service chatbot with:
✅ Comprehensive testing (147 tests, 89%+ coverage)
✅ Strong security (all vulnerabilities resolved)
✅ Excellent performance (meets all SLOs)
✅ Full accessibility compliance (WCAG 2.1 AA)
✅ Complete operational readiness (monitoring, runbooks, rollback plan)

Risks are well-mitigated with progressive canary deployment and tested rollback.

═══════════════════════════════════════════════════════════════

👤 APPROVAL REQUIRED FROM:

[ ] Engineering Lead (@alice) - Technical approval
[ ] Product Manager (@bob) - Business approval
[ ] Security Lead (@eve) - Security sign-off

**To approve this release, please confirm:**
1. You have reviewed the quality gates and risk assessment
2. You approve the deployment strategy and timeline
3. You acknowledge the monitoring plan and rollback procedure
4. You authorize proceeding with production deployment

**Please respond with one of:**
- "APPROVED" - Proceed with deployment as planned
- "APPROVED WITH CONDITIONS" - Proceed with specified modifications
- "REJECTED" - Do not deploy, provide reasoning

═══════════════════════════════════════════════════════════════

APPROVAL RESPONSES:

@alice (Engineering Lead):
"APPROVED - Technical review complete. All quality gates met.
Canary strategy is appropriate. Team ready to monitor."
Timestamp: 2024-01-24 14:30 PST

@bob (Product Manager):
"APPROVED - Business value confirmed. Customer support briefed.
Excited to see this go live!"
Timestamp: 2024-01-24 14:35 PST

@eve (Security Lead):
"APPROVED - Security assessment passed. All high/critical
vulnerabilities resolved. Monitoring in place for anomaly detection."
Timestamp: 2024-01-24 14:40 PST

═══════════════════════════════════════════════════════════════

✅ RELEASE APPROVED FOR PRODUCTION DEPLOYMENT

Final Approvals: 3/3
Status: AUTHORIZED
Deployment Scheduled: Tuesday, January 25, 2024, 10:00 AM PST
Next Step: Begin canary deployment (Phase 1: 10%)
```

---

### Step 6: Operations Infrastructure

**Command:**
```bash
/jpspec:operate AI customer service chatbot
```

**What happens:**
- **SRE agent** designs and implements comprehensive operational infrastructure
- Sets up CI/CD pipelines, Kubernetes deployments, observability stack, and incident management procedures

**Deliverables:**
- GitHub Actions CI/CD workflows
- Kubernetes deployment manifests
- Observability stack configuration (Prometheus, Grafana, Loki, Jaeger)
- Runbooks and operational procedures
- Incident response plan
- SLI/SLO definitions

**Output includes:**

*CI/CD Pipeline:*
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
      - name: Security scan
        run: npm audit --audit-level=high

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t chatbot:${{ github.sha }} .
      - name: Push to registry
        run: docker push chatbot:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy canary (10%)
        run: kubectl apply -f k8s/canary.yaml
      - name: Monitor canary
        run: ./scripts/monitor-canary.sh
      - name: Deploy production (100%)
        if: success()
        run: kubectl apply -f k8s/production.yaml
```

*Kubernetes Deployment:*
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-api
  labels:
    app: chatbot
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: chatbot
  template:
    metadata:
      labels:
        app: chatbot
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
      containers:
      - name: api
        image: chatbot:latest
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            Port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: openai-api-key
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chatbot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chatbot-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

*SLI/SLO Definitions:*
```
SERVICE LEVEL OBJECTIVES (SLOs)

Availability: 99.9% uptime
- SLI: % of successful HTTP requests (status code < 500)
- Error Budget: 43 minutes downtime per month

Latency: p95 < 200ms
- SLI: 95th percentile response time
- Measurement: API Gateway to response

Throughput: Support 1,000 req/s
- SLI: Requests per second handled without errors
- Measurement: Peak load capacity

Error Rate: < 0.1%
- SLI: % of requests returning errors
- Measurement: 5xx errors / total requests
```

*Runbook Example:*
```markdown
## Runbook: High Latency Alert

### Symptoms
- p95 latency > 500ms for 5+ minutes
- User complaints about slow responses

### Investigation Steps
1. Check Grafana dashboard: https://grafana.company.com/d/chatbot
2. Review error logs: kubectl logs -l app=chatbot --tail=100
3. Check LLM API status: curl https://status.openai.com/api/v2/status.json
4. Verify database connection pool: kubectl exec -it chatbot-xxx -- /app/debug/pool-stats

### Common Causes
- LLM API degradation → Check circuit breaker metrics
- Database connection exhaustion → Check pool size
- High traffic spike → Check HPA scaling

### Resolution
- If LLM API degraded: Enable response caching, increase timeout
- If DB connection issue: Restart pods, increase pool size
- If traffic spike: Manually scale replicas

### Escalation
If not resolved in 15 minutes: Page on-call engineer via PagerDuty
```

*Actual CI/CD Pipeline Execution:*

```bash
# GitHub Actions execution log for v1.2.0 deployment
# Date: 2024-01-25 10:00 AM PST

Run #459 - Deploy to Production
Triggered by: push to main (commit: a3f9bc8)
Branch: main
Commit message: "feat: AI customer service chatbot with sentiment analysis"

═══════════════════════════════════════════════════════════════

[10:00:15] ▶ Job: test
[10:00:16] ✓ Checkout code (actions/checkout@v4)
[10:00:18] ▶ Setup Node.js 20.x
[10:00:22] ✓ Node.js setup complete
[10:00:23] ▶ Install dependencies
[10:00:45] ✓ Dependencies installed (347 packages)

[10:00:46] ▶ Run unit tests (frontend)
[10:00:48] PASS src/components/__tests__/ChatWidget.test.tsx
[10:00:48]   ChatWidget
[10:00:48]     ✓ should render messages correctly (45ms)
[10:00:48]     ✓ should send message on submit (89ms)
[10:00:48]     ✓ should clear input after sending (62ms)
[10:00:48]     ✓ should disable input while loading (12ms)
[10:00:48]     ✓ should be keyboard accessible (103ms)
[10:00:49]
[10:00:49] Test Suites: 23 passed, 23 total
[10:00:49] Tests:       147 passed, 147 total
[10:00:49] Snapshots:   0 total
[10:00:49] Time:        3.421s
[10:00:49] ✓ Frontend tests passed

[10:00:50] ▶ Run integration tests (backend)
[10:00:52] === RUN   TestProcessMessage_HappyPath
[10:00:52] --- PASS: TestProcessMessage_HappyPath (0.12s)
[10:00:52] === RUN   TestProcessMessage_NegativeSentimentEscalation
[10:00:52] --- PASS: TestProcessMessage_NegativeSentimentEscalation (0.08s)
[10:00:53] === RUN   TestProcessMessage_InvalidInput
[10:00:53] --- PASS: TestProcessMessage_InvalidInput (0.02s)
[10:00:53] PASS
[10:00:53] coverage: 92.3% of statements
[10:00:53] ok      github.com/chatbot/internal/conversation    0.387s
[10:00:53] ✓ Backend tests passed

[10:00:54] ▶ Security scan (npm audit)
[10:00:56] found 0 vulnerabilities in 347 packages
[10:00:56] ✓ Security scan clean

[10:00:57] ▶ Trivy container scan
[10:00:59] Total: 0 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0)
[10:00:59] ✓ Container scan clean

[10:01:00] ✅ Job: test completed successfully (Duration: 45s)

═══════════════════════════════════════════════════════════════

[10:01:05] ▶ Job: build
[10:01:06] ✓ Checkout code
[10:01:08] ▶ Setup Docker Buildx
[10:01:10] ✓ Docker Buildx ready

[10:01:11] ▶ Build Docker image (chatbot:a3f9bc8)
[10:01:12] #1 [internal] load build definition from Dockerfile
[10:01:12] #1 transferring dockerfile: 892B done
[10:01:13] #2 [internal] load .dockerignore
[10:01:13] #2 transferring context: 45B done
[10:01:14] #3 [internal] load metadata for docker.io/library/node:20-alpine
[10:01:16] #3 DONE 1.8s
[10:01:17] #4 [stage-1 1/6] FROM docker.io/library/node:20-alpine@sha256:abc123...
[10:01:20] #4 CACHED
[10:01:20] #5 [stage-1 2/6] WORKDIR /app
[10:01:20] #5 CACHED
[10:01:21] #6 [stage-1 3/6] COPY package*.json ./
[10:01:22] #6 DONE 0.4s
[10:01:22] #7 [stage-1 4/6] RUN npm ci --only=production
[10:02:15] #7 DONE 52.8s
[10:02:16] #8 [stage-1 5/6] COPY . .
[10:02:18] #8 DONE 2.1s
[10:02:18] #9 [stage-1 6/6] RUN npm run build
[10:03:45] #9 DONE 87.3s
[10:03:46] #10 exporting to image
[10:03:48] #10 exporting layers done
[10:03:48] #10 writing image sha256:def456... done
[10:03:48] #10 naming to docker.io/chatbot:a3f9bc8 done
[10:03:48] ✓ Docker image built successfully

[10:03:49] ▶ Push to container registry
[10:03:50] The push refers to repository [registry.company.com/chatbot]
[10:03:51] a3f9bc8e72d1: Preparing
[10:03:52] b2c3d4e5f6a7: Preparing
[10:04:05] a3f9bc8e72d1: Pushed
[10:04:12] b2c3d4e5f6a7: Pushed
[10:04:13] a3f9bc8: digest: sha256:ghi789... size: 2847
[10:04:13] ✓ Image pushed successfully

[10:04:14] ✅ Job: build completed successfully (Duration: 3m 9s)

═══════════════════════════════════════════════════════════════

[10:04:20] ▶ Job: deploy
[10:04:21] ✓ Checkout code
[10:04:23] ▶ Configure kubectl (GKE production cluster)
[10:04:25] ✓ kubectl configured

[10:04:26] ▶ Deploy canary (10% traffic)
[10:04:27] $ kubectl apply -f k8s/canary.yaml
[10:04:28] deployment.apps/chatbot-api-canary configured
[10:04:28] service/chatbot-canary configured
[10:04:28] virtualservice.networking.istio.io/chatbot-canary configured
[10:04:28]   - 90% traffic → chatbot-api (stable)
[10:04:28]   - 10% traffic → chatbot-api-canary (v1.2.0)
[10:04:29] ✓ Canary deployed

[10:04:30] ▶ Wait for canary pods to be ready
[10:04:35] pod/chatbot-api-canary-7d9f8b6c5-x7k9m condition met
[10:04:35] pod/chatbot-api-canary-7d9f8b6c5-y2p4n condition met
[10:04:35] ✓ Canary pods ready (2/2)

[10:04:36] ▶ Monitor canary metrics (30 minutes)
[10:04:40] [+0:00] Canary health: ✅ GREEN
[10:04:40]   - Error rate: 0.00% (target: <0.5%)
[10:04:40]   - p95 latency: 165ms (target: <300ms)
[10:04:40]   - Request rate: 12.4 req/s (~10% of total)
[10:09:40] [+5:00] Canary health: ✅ GREEN
[10:09:40]   - Error rate: 0.02% (target: <0.5%)
[10:09:40]   - p95 latency: 178ms (target: <300ms)
[10:09:40]   - Request rate: 13.1 req/s
[10:14:40] [+10:00] Canary health: ✅ GREEN
[10:14:40]   - Error rate: 0.01% (target: <0.5%)
[10:14:40]   - p95 latency: 172ms (target: <300ms)
[10:14:40]   - User escalation rate: 7.2% (expected: 5-10%)
[10:19:40] [+15:00] Canary health: ✅ GREEN
[10:24:40] [+20:00] Canary health: ✅ GREEN
[10:29:40] [+25:00] Canary health: ✅ GREEN
[10:34:40] [+30:00] Canary health: ✅ GREEN
[10:34:40]   - Total requests served: 22,847
[10:34:40]   - Successful: 22,843 (99.98%)
[10:34:40]   - Failed: 4 (0.02%)
[10:34:41] ✓ Canary metrics healthy for 30 minutes

[10:34:42] ▶ Promote canary to 50% traffic
[10:34:43] $ kubectl patch virtualservice chatbot-canary --type merge -p '{"spec":{"http":[{"route":[{"destination":{"host":"chatbot","subset":"stable"},"weight":50},{"destination":{"host":"chatbot","subset":"canary"},"weight":50}]}]}}'
[10:34:44] virtualservice.networking.istio.io/chatbot-canary patched
[10:34:44] ✓ Traffic split: 50% stable / 50% canary

[10:34:45] ▶ Scale canary to handle 50% traffic
[10:34:46] $ kubectl scale deployment chatbot-api-canary --replicas=10
[10:34:47] deployment.apps/chatbot-api-canary scaled
[10:35:15] ✓ Canary scaled to 10 replicas

[10:35:16] ▶ Monitor canary at 50% (1 hour)
[10:40:16] [+5:00] Canary health: ✅ GREEN (50% traffic)
[10:40:16]   - Error rate: 0.03% (target: <0.5%)
[10:40:16]   - p95 latency: 183ms (target: <300ms)
[10:40:16]   - Request rate: 62.1 req/s (~50% of total)
[11:05:16] [+30:00] Canary health: ✅ GREEN
[11:05:16]   - Error rate: 0.02% (target: <0.5%)
[11:05:16]   - p95 latency: 189ms (target: <300ms)
[11:05:16]   - Sentiment model accuracy: 94.3%
[11:05:16]   - Circuit breaker state: CLOSED (healthy)
[11:35:16] [+60:00] Canary health: ✅ GREEN
[11:35:16]   - Total requests: 224,518
[11:35:16]   - Success rate: 99.97%
[11:35:16] ✓ Canary metrics healthy for 1 hour at 50% traffic

[11:35:17] ▶ Promote canary to 100% (full rollout)
[11:35:18] $ kubectl set image deployment/chatbot-api api=registry.company.com/chatbot:a3f9bc8
[11:35:19] deployment.apps/chatbot-api image updated
[11:35:20] $ kubectl rollout status deployment/chatbot-api
[11:35:25] Waiting for deployment "chatbot-api" rollout to finish: 3 of 20 updated replicas are available...
[11:36:15] Waiting for deployment "chatbot-api" rollout to finish: 15 of 20 updated replicas are available...
[11:37:45] deployment "chatbot-api" successfully rolled out
[11:37:45] ✓ All 20 pods running v1.2.0

[11:37:46] ▶ Remove canary deployment
[11:37:47] $ kubectl delete deployment chatbot-api-canary
[11:37:48] deployment.apps "chatbot-api-canary" deleted
[11:37:48] ✓ Canary cleanup complete

[11:37:49] ▶ Post-deployment verification
[11:37:50] $ curl -s https://api.chatbot.example.com/health | jq .
[11:37:51] {
[11:37:51]   "status": "healthy",
[11:37:51]   "version": "v1.2.0",
[11:37:51]   "uptime": "2m15s",
[11:37:51]   "checks": {
[11:37:51]     "database": "healthy",
[11:37:51]     "redis": "healthy",
[11:37:51]     "llm_api": "healthy"
[11:37:51]   }
[11:37:51] }
[11:37:52] ✓ Health check passed

[11:37:53] ▶ Verify metrics endpoint
[11:37:54] $ curl -s https://api.chatbot.example.com/metrics | grep chatbot_requests_total
[11:37:55] chatbot_requests_total{status="success"} 247365
[11:37:55] chatbot_requests_total{status="error"} 78
[11:37:55] ✓ Metrics endpoint responding

[11:37:56] ✅ Job: deploy completed successfully (Duration: 1h 33m 36s)

═══════════════════════════════════════════════════════════════

✅ DEPLOYMENT COMPLETE

Summary:
- Version: v1.2.0 (commit: a3f9bc8)
- Duration: 1h 37m 51s
- Tests: 147 passed, 0 failed
- Security scans: Clean
- Canary phases: 10% (30min) → 50% (1hr) → 100%
- Final status: SUCCESS
- Pods running: 20/20
- Health checks: All passing

Next steps:
- Monitor for 4 hours (extended observation)
- Review error budget consumption
- Collect user feedback

Deployment URL: https://app.chatbot.example.com
Monitoring: https://grafana.company.com/d/chatbot-realtime
```

*Monitoring & Observability in Action:*

**Prometheus Query Examples:**
```promql
# Error rate over last 5 minutes
sum(rate(http_requests_total{job="chatbot-api",status=~"5.."}[5m]))
/
sum(rate(http_requests_total{job="chatbot-api"}[5m]))
* 100

# Result: 0.023% (✅ within SLO of <0.1%)

# p95 latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket{job="chatbot-api"}[5m])) by (le)
)

# Result: 0.187 seconds = 187ms (✅ within SLO of <200ms)

# Circuit breaker state
chatbot_circuit_breaker_state{service="llm_api"}
# Result: 0 (CLOSED - healthy), 1 = OPEN (failing)

# Sentiment analysis accuracy (based on human feedback)
sum(chatbot_sentiment_correct_total) / sum(chatbot_sentiment_checked_total) * 100
# Result: 94.3%

# Error budget remaining (30-day window)
(1 - (sum(rate(http_requests_total{status=~"5.."}[30d]))
      / sum(rate(http_requests_total[30d])))) - 0.999
# Result: 0.00077 = 0.077% remaining (33.2 minutes of 43.2 minutes)
```

**Grafana Dashboard - Real-Time Metrics:**
```
┌─────────────────────────────────────────────────────────────────┐
│ AI Chatbot - Production Dashboard         Last 15 minutes      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│ │ Request Rate │  │ Error Rate   │  │ p95 Latency  │         │
│ │   124.7/s    │  │   0.023%     │  │   187ms      │         │
│ │      ✅      │  │      ✅      │  │      ✅      │         │
│ └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│ │ Active Pods  │  │ CPU Usage    │  │ Memory Usage │         │
│ │    20/20     │  │    67%       │  │   1.2GB/2GB  │         │
│ │      ✅      │  │      ✅      │  │      ✅      │         │
│ └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│ Request Rate (last hour)                                       │
│  150 ┤                             ╭─╮                         │
│  125 ┤                      ╭──────╯ ╰─╮                       │
│  100 ┤              ╭───────╯         ╰─────╮                  │
│   75 ┤         ╭────╯                       ╰────╮             │
│   50 ┤    ╭────╯                                 ╰───╮         │
│   25 ┤────╯                                          ╰────     │
│      └──┬────┬────┬────┬────┬────┬────┬────┬────┬────┬──     │
│        11:00  11:15  11:30  11:45  12:00  12:15  12:30        │
│                                                                 │
│ Error Rate % (last hour)                                       │
│ 0.10 ┤ SLO Threshold ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│ 0.08 ┤                                                         │
│ 0.06 ┤                                                         │
│ 0.04 ┤         ╭╮                                              │
│ 0.02 ┤     ╭───╯╰───╮  ╭╮        ╭─╮                         │
│ 0.00 ┤─────╯        ╰──╯╰────────╯ ╰─────────────────────    │
│      └──┬────┬────┬────┬────┬────┬────┬────┬────┬────┬──     │
│        11:00  11:15  11:30  11:45  12:00  12:15  12:30        │
│                                                                 │
│ Top Errors (last hour)                                         │
│ 1. LLM API timeout                    47 occurrences (60%)    │
│ 2. Rate limit exceeded                23 occurrences (29%)    │
│ 3. Database connection timeout         8 occurrences (10%)    │
│                                                                 │
│ Circuit Breaker Status                                         │
│ LLM API: ● CLOSED (healthy)           Failures: 0/3           │
│ Database: ● CLOSED (healthy)          Failures: 0/3           │
│                                                                 │
│ SLO Compliance (30-day window)                                │
│ Availability: 99.923% ✅ (SLO: 99.9%)                         │
│ Error Budget: 33.2 min remaining of 43.2 min (77% remaining)  │
│ Burn Rate: 0.3x (healthy - well under alert threshold of 14x) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Alert Configuration (Prometheus AlertManager):**
```yaml
groups:
- name: chatbot-slo-alerts
  interval: 1m
  rules:
    - alert: HighErrorRate
      expr: |
        sum(rate(http_requests_total{job="chatbot-api",status=~"5.."}[5m]))
        / sum(rate(http_requests_total{job="chatbot-api"}[5m]))
        > 0.01
      for: 5m
      labels:
        severity: critical
        component: chatbot-api
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value | humanizePercentage }} (threshold: 1%)"
        runbook: "https://runbooks.company.com/chatbot/high-error-rate"
        dashboard: "https://grafana.company.com/d/chatbot-realtime"

    - alert: HighLatency
      expr: |
        histogram_quantile(0.95,
          sum(rate(http_request_duration_seconds_bucket{job="chatbot-api"}[5m])) by (le)
        ) > 0.3
      for: 10m
      labels:
        severity: warning
        component: chatbot-api
      annotations:
        summary: "High p95 latency detected"
        description: "p95 latency is {{ $value | humanizeDuration }} (threshold: 300ms)"

    - alert: ErrorBudgetBurnRateHigh
      expr: |
        (1 - (sum(rate(http_requests_total{status=~"5.."}[1h]))
              / sum(rate(http_requests_total[1h])))) - 0.999
        < 0
      labels:
        severity: critical
      annotations:
        summary: "Error budget burning too fast"
        description: "At current rate, error budget will be exhausted in < 2 days"
```

*Incident Response Example:*

```markdown
INCIDENT REPORT #INC-2847
Incident: LLM API Circuit Breaker Open
Date: 2024-01-26 14:23 PST
Severity: HIGH (user-impacting)
Duration: 12 minutes
Status: RESOLVED

═══════════════════════════════════════════════════════════════

TIMELINE:

14:23:15 - 🔴 Alert fired: "ChatbotCircuitBreakerOpen"
           Grafana alert: LLM API circuit breaker state = OPEN
           PagerDuty notification sent to on-call SRE @dave

14:24:30 - 👤 @dave acknowledged incident
           Investigating via runbook: circuit-breaker-open

14:25:00 - 🔍 Investigation findings:
           - OpenAI API status: DEGRADED (confirmed via status.openai.com)
           - Last 3 LLM requests failed with 503 Service Unavailable
           - Circuit breaker correctly opened after 3 failures
           - Fallback responses being served to users

14:26:00 - 💬 Communication:
           Posted in #incidents Slack channel:
           "LLM API degraded, circuit breaker open. Users receiving
            fallback responses. Monitoring OpenAI status page."

14:28:00 - 📊 Metrics check:
           - Error rate: 0.3% (slightly elevated but < 1% threshold)
           - User impact: ~15% of requests using fallback responses
           - Escalation rate: 42% (elevated - expected 5-10%)
           - No user complaints in support channels yet

14:30:00 - ✅ OpenAI API recovery detected
           OpenAI status page: DEGRADED → OPERATIONAL

14:31:00 - 🔄 Circuit breaker attempting recovery
           Test request to LLM API: SUCCESS
           Circuit breaker: OPEN → HALF-OPEN

14:32:00 - ✅ Circuit breaker fully recovered
           3 consecutive successful requests
           Circuit breaker: HALF-OPEN → CLOSED

14:33:00 - 📈 Metrics verification:
           - Error rate: 0.05% (back to normal)
           - p95 latency: 195ms (healthy)
           - Escalation rate: 8% (back to normal range)
           - LLM API success rate: 99.8%

14:35:00 - ✅ Incident resolved
           All systems operational
           Monitoring for 30 min to ensure stability

15:05:00 - 📝 Post-incident update:
           No recurrence. Metrics stable.
           Incident closed.

═══════════════════════════════════════════════════════════════

ROOT CAUSE:

Upstream OpenAI API experienced brief degradation (confirmed on
their status page). This was an external dependency issue, not a
problem with our system.

IMPACT:

- Duration: 12 minutes
- User impact: ~15% of requests served fallback responses
- Escalation to human agents: Temporarily elevated to 42%
- Error budget consumed: 3.7 minutes (8.6% of monthly budget)
- Customer complaints: 0 (fallback UX worked well)

WHAT WENT WELL:

✅ Circuit breaker worked exactly as designed
✅ Fallback responses prevented user-facing errors
✅ Automatic recovery when API restored
✅ Monitoring and alerting caught issue immediately
✅ Runbook provided clear investigation path
✅ No manual intervention required (self-healing)

WHAT COULD BE IMPROVED:

⚠️ Escalation rate spiked to 42% during fallback mode
   - Fallback message "technical difficulties" triggered
     sentiment-based escalation
   - Action: Improve fallback message wording (INC-2847-A1)

⚠️ No proactive notification to users about degraded service
   - Users weren't aware of temporary limitations
   - Action: Add in-app banner when circuit breaker opens (INC-2847-A2)

ACTION ITEMS:

[ ] INC-2847-A1: Update fallback message to be less alarming
    - Assignee: @alice
    - Due: 2024-01-29
    - Priority: Medium
    - Estimated effort: 1 hour

[ ] INC-2847-A2: Implement in-app banner for degraded mode
    - Assignee: @bob
    - Due: 2024-02-05
    - Priority: Low
    - Estimated effort: 4 hours

[ ] INC-2847-A3: Add OpenAI API status to internal dashboard
    - Assignee: @dave
    - Due: 2024-02-01
    - Priority: Low
    - Estimated effort: 2 hours

POST-MORTEM SCHEDULED:

Date: 2024-01-27 10:00 AM PST
Attendees: Engineering team, SRE, Product
Agenda: Review incident, discuss improvements, update runbooks
```

*Error Budget Tracking:*

```markdown
ERROR BUDGET REPORT - JANUARY 2024
Service: AI Customer Service Chatbot
SLO: 99.9% availability (43.2 minutes downtime allowed per 30 days)

═══════════════════════════════════════════════════════════════

ERROR BUDGET STATUS (as of 2024-01-26):

Budget Remaining: 33.2 minutes (76.9%)
Budget Consumed: 10.0 minutes (23.1%)
Burn Rate: 0.3x (healthy - sustainable for full month)

┌─────────────────────────────────────────────────────────────┐
│ Error Budget Visualization (30-day rolling window)         │
│                                                             │
│ 43.2 min ┤█████████████████████████████████░░░░░░░░░░░     │
│          │                                                 │
│  Consumed: ████████ 10.0 min (23.1%)                      │
│  Remaining: ░░░░░░░░░░░░░░░░░░░░░░░░░ 33.2 min (76.9%)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

BUDGET CONSUMPTION BY INCIDENT:

1. INC-2847 (Jan 26): LLM API Circuit Breaker     3.7 min (37%)
2. INC-2801 (Jan 19): Database Connection Pool    4.2 min (42%)
3. INC-2756 (Jan 12): Kubernetes Node Failure     2.1 min (21%)
   ────────────────────────────────────────────────────────
   TOTAL:                                         10.0 min (100%)

BURN RATE ANALYSIS:

Current burn rate: 0.3x (10 min consumed over 26 days)
Projected end-of-month: 11.5 min consumed (26.6% of budget)
Status: ✅ HEALTHY (well within budget)

Alert thresholds:
⚠️ Warning: Burn rate > 5x (would exhaust budget in 6 days)
🔴 Critical: Burn rate > 14x (would exhaust budget in 2 days)

RECOMMENDATIONS:

✅ Error budget healthy - no action required
✅ Incident response effective (avg resolution: 15 minutes)
✅ Circuit breaker preventing budget exhaustion
💡 Consider: Set up automated responses for common failure modes

HISTORICAL TREND (last 6 months):

Sep 2023: 8.5 min consumed (19.7%) ✅
Oct 2023: 12.1 min consumed (28.0%) ✅
Nov 2023: 15.3 min consumed (35.4%) ⚠️
Dec 2023: 9.8 min consumed (22.7%) ✅
Jan 2024: 10.0 min consumed (23.1%) ✅ (projected: 11.5 min)

Trend: STABLE - monthly consumption typically 20-30% of budget
```

---

## Command Reference

### /jpspec:research

**Purpose:** Conduct comprehensive market research and business validation.

**Agents Used:**
1. **researcher** (Phase 1) - Market analysis, competitive landscape, technical feasibility
2. **business-validator** (Phase 2) - Financial viability, opportunity assessment, risk analysis

**Execution:** Sequential (validator uses researcher's output)

**Input Format:**
```bash
/jpspec:research <project description>
```

**Example:**
```bash
/jpspec:research AI-powered code review tool for enterprise development teams
```

**Output:**
- Research report with market sizing, competitive analysis, technical assessment
- Business validation report with Go/No-Go recommendation
- Opportunity score (1-10) with detailed breakdown
- Risk register and mitigation strategies

**When to Use:**
- Starting a new project or product
- Evaluating a feature idea before investing resources
- Need data-driven decision making
- Want to understand market dynamics and competition

---

### /jpspec:specify

**Purpose:** Create comprehensive product requirements and task breakdown.

**Agents Used:**
1. **product-requirements-manager-enhanced** - PRD creation, user stories, acceptance criteria

**Input Format:**
```bash
/jpspec:specify <feature description> [context from research]
```

**Example:**
```bash
/jpspec:specify Authentication system with OAuth2, SSO, and MFA based on enterprise security requirements
```

**Output:**
- Complete Product Requirement Document (PRD)
- User stories with acceptance criteria
- Task breakdown organized by epic
- Success metrics and KPIs
- Populated `/speckit.tasks` for tracking

**When to Use:**
- After research validation confirms viability
- Need detailed requirements before architecture
- Want to align stakeholders on scope
- Preparing for sprint planning

---

### /jpspec:plan

**Purpose:** Design system architecture and platform infrastructure.

**Agents Used:**
1. **software-architect-enhanced** (Parallel) - System architecture, component design, ADRs
2. **platform-engineer-enhanced** (Parallel) - CI/CD, Kubernetes, observability, security

**Execution:** Parallel for maximum efficiency

**Input Format:**
```bash
/jpspec:plan <project name> [PRD and requirements]
```

**Example:**
```bash
/jpspec:plan E-commerce checkout system with payment processing and inventory management
```

**Output:**
- System architecture diagrams and component design
- Architecture Decision Records (ADRs)
- Platform infrastructure design
- CI/CD pipeline architecture
- Updated `/speckit.constitution` with principles and standards

**When to Use:**
- After specifications are complete
- Before implementation begins
- Need to align on technical approach
- Want to document architectural decisions

---

### /jpspec:implement

**Purpose:** Implement features with specialized engineers and code review.

**Agents Used:**

**Phase 1 - Implementation (Parallel):**
- **frontend-engineer** - React/React Native UI development (if UI needed)
- **backend-engineer** - API services in Go/TypeScript/Python (if backend needed)
- **ai-ml-engineer** - ML models and inference services (if ML needed)

**Phase 2 - Code Review (Sequential):**
- **frontend-code-reviewer** - UI code review (follows frontend implementation)
- **backend-code-reviewer** - API code review (follows backend implementation)

**Input Format:**
```bash
/jpspec:implement <feature description> [architecture and specs]
```

**Example:**
```bash
/jpspec:implement Real-time notification system with WebSocket support and push notifications
```

**Output:**
- Production-ready code (frontend/backend/ML as applicable)
- Comprehensive test suites
- Code review reports with prioritized feedback
- Implementation documentation

**When to Use:**
- After architecture and planning complete
- Ready to write production code
- Want automated code review
- Need consistent quality standards

**Notes:**
- System determines which engineers to use based on feature requirements
- Code review runs automatically after implementation
- Iteration may be needed to address review feedback

---

### /jpspec:validate

**Purpose:** Comprehensive quality assurance, security validation, and release management.

**Agents Used:**

**Phase 1 - Testing & Security (Parallel):**
- **quality-guardian** - Functional, integration, performance, accessibility testing
- **secure-by-design-engineer** - Security assessment, vulnerability scanning, compliance

**Phase 2 - Documentation (Sequential):**
- **tech-writer** - API docs, user guides, runbooks, release notes

**Phase 3 - Release Management (Final Gate):**
- **release-manager** - Release readiness, deployment planning, **human approval request**

**Input Format:**
```bash
/jpspec:validate <feature name> [code and artifacts]
```

**Example:**
```bash
/jpspec:validate Payment processing API with PCI DSS compliance requirements
```

**Output:**
- QA test report with quality metrics
- Security assessment with vulnerability findings
- Complete documentation package
- Release readiness assessment
- **Human approval checkpoint** before production

**When to Use:**
- Implementation complete and reviewed
- Ready for pre-production validation
- Need security clearance
- Preparing for production release

**Important:** Phase 3 requires explicit human approval before proceeding to deployment.

---

### /jpspec:operate

**Purpose:** Design and implement operational infrastructure for production.

**Agents Used:**
1. **sre-agent** - CI/CD, Kubernetes, observability, incident management, DR planning

**Input Format:**
```bash
/jpspec:operate <project name> [architecture and platform specs]
```

**Example:**
```bash
/jpspec:operate Microservices platform with multi-region deployment and 99.99% SLA
```

**Output:**
- GitHub Actions CI/CD workflows
- Kubernetes deployment manifests
- Observability stack (Prometheus, Grafana, Loki, Jaeger)
- Alerting rules and dashboards
- Runbooks and incident response procedures
- SLI/SLO definitions
- Disaster recovery plan

**When to Use:**
- After validation phase complete
- Ready to set up production infrastructure
- Need operational procedures
- Want SRE best practices applied

**Operational Excellence:** Applies DORA Elite Performance metrics, SRE principles, and DevSecOps practices.

---

## Multi-Agent Architecture

jpspec uses a sophisticated multi-agent orchestration system that coordinates specialized AI agents across the software delivery lifecycle.

### How It Works

**Agent Specialization**
Each agent is an expert in a specific domain:
- **researcher**: Market analysis, competitive intelligence
- **business-validator**: Financial modeling, opportunity assessment
- **product-requirements-manager-enhanced**: PRD creation, requirements engineering
- **software-architect-enhanced**: System design applying Gregor Hohpe's Enterprise Integration Patterns
- **platform-engineer-enhanced**: DevOps, platform engineering, DORA metrics
- **frontend-engineer**: React/React Native, TypeScript, accessibility
- **backend-engineer**: API design, Go/Node.js/Python, database optimization
- **ai-ml-engineer**: ML pipelines, model deployment, MLOps
- **frontend-code-reviewer**: UI code review, performance, accessibility
- **backend-code-reviewer**: API security, performance, code quality
- **quality-guardian**: Testing strategy, QA automation, risk analysis
- **secure-by-design-engineer**: Security assessment, vulnerability scanning, compliance
- **tech-writer**: Documentation, API references, user guides
- **release-manager**: Release planning, deployment coordination, approval gates
- **sre-agent**: SRE practices, observability, incident management

### Orchestration Patterns

**Sequential Execution**
Agents run one after another, with later agents using earlier outputs:
```
researcher → business-validator
(research findings feed into validation)

frontend-engineer → frontend-code-reviewer
(implementation must complete before review)
```

**Parallel Execution**
Independent agents run simultaneously for speed:
```
software-architect-enhanced ┐
                            ├→ consolidation
platform-engineer-enhanced  ┘

quality-guardian           ┐
                           ├→ validation report
secure-by-design-engineer  ┘
```

**Phased Execution**
Multiple phases with different orchestration patterns:
```
Phase 1 (Parallel):    frontend-engineer + backend-engineer
Phase 2 (Sequential):  frontend-code-reviewer → backend-code-reviewer
Phase 3 (Integration): consolidate and deploy
```

### Agent Communication

Agents communicate through:
1. **Shared Context**: Previous agents' outputs become next agents' inputs
2. **Artifacts**: Documents stored in `/speckit.tasks` and `/speckit.constitution`
3. **Standards**: Shared principles and constraints guide all agents

### Quality Gates

Each workflow includes quality gates:
- **Research**: Business validation score must meet threshold
- **Planning**: Architecture must satisfy constraints
- **Implementation**: Code review must pass critical checks
- **Validation**: Security and QA must approve
- **Release**: Human approval required before production

---

## Best Practices

### 1. Follow the Workflow Sequence

**Do:** Execute workflows in order
```bash
/jpspec:research <idea>      # Start here
/jpspec:specify <idea>       # Then specify
/jpspec:plan <idea>          # Then plan
/jpspec:implement <idea>     # Then implement
/jpspec:validate <idea>      # Then validate
/jpspec:operate <idea>       # Finally operate
```

**Why:** Each phase builds on previous outputs. Skipping phases leads to gaps and rework.

**Exception:** For existing projects, you can start at any phase if you have the required context from previous phases.

---

### 2. Provide Rich Context

**Do:** Include relevant background
```bash
/jpspec:specify Real-time collaborative document editor with operational transformation,
based on research showing 5M TAM and competitive differentiation through superior conflict resolution
```

**Don't:** Give minimal information
```bash
/jpspec:specify Document editor
```

**Why:** More context enables agents to make better decisions and produce higher-quality outputs.

---

### 3. Use Research to Validate Ideas

**Do:** Run research before investing in development
```bash
/jpspec:research Blockchain-based supply chain tracking for pharmaceutical industry
# Review business-validator recommendation before proceeding
```

**Why:** Research reveals market dynamics, competition, and viability. A "No-Go" recommendation saves wasted effort.

---

### 4. Review and Iterate on Specifications

**Do:** Carefully review the PRD from `/jpspec:specify`
- Verify user stories match your vision
- Check acceptance criteria are complete
- Validate non-functional requirements (performance, security, accessibility)
- Refine and run again if needed

**Why:** Specifications guide all downstream work. Errors here cascade through implementation.

---

### 5. Save Architecture Decision Records

**Do:** Preserve ADRs from `/jpspec:plan` in your repository
```bash
# ADRs document key decisions with rationale
docs/architecture/adr-001-database-selection.md
docs/architecture/adr-002-api-architecture.md
```

**Why:** Future team members need to understand why decisions were made. ADRs prevent relitigating settled choices.

---

### 6. Address Code Review Feedback

**Do:** Fix Critical and High priority issues before proceeding
```
Code Review: backend-api
❌ CRITICAL: SQL injection vulnerability in user query endpoint
⚠️ HIGH: Missing rate limiting allows abuse
✅ MEDIUM: Consider adding response caching
```

**Don't:** Ignore review feedback and proceed to validation

**Why:** Critical issues become production incidents. High priority issues cause technical debt.

---

### 7. Take Human Approval Gates Seriously

**Do:** Carefully review release readiness assessment
```
🚦 HUMAN APPROVAL REQUIRED

Quality: ✅ 98% test pass rate
Security: ⚠️ 2 medium vulnerabilities (fixes ready)
Performance: ✅ Meets all SLOs
Documentation: ✅ Complete

Risk: MEDIUM (customer-facing changes)
Rollback: LOW complexity

[Review all details before approving]
```

**Don't:** Rubber-stamp approvals without reading

**Why:** You're accountable for production issues. The approval gate protects your users and business.

---

### 8. Customize Workflows for Your Needs

**Do:** Skip optional phases or customize prompts
```bash
# For backend-only features, implementation will skip frontend agents
/jpspec:implement Background job processing system

# For prototypes, skip operations
/jpspec:research → specify → plan → implement
(skip validate and operate for faster iteration)
```

**Why:** Not every project needs every phase. Adapt the workflow to your context.

---

### 9. Leverage Parallel Execution

**Note:** jpspec automatically runs agents in parallel when possible
- `/jpspec:plan`: Architecture + Platform (parallel)
- `/jpspec:implement`: Frontend + Backend + ML (parallel)
- `/jpspec:validate`: QA + Security (parallel)

**Why:** Parallel execution reduces end-to-end time significantly.

---

### 10. Maintain /speckit Artifacts

**Do:** Keep `/speckit.tasks` and `/speckit.constitution` updated
- `/speckit.tasks`: Task breakdown and backlog (from specify)
- `/speckit.constitution`: Architectural principles and standards (from plan)

**Why:** These artifacts provide consistency across iterations and team members.

---

## Troubleshooting

### Issue: "Agent produced incomplete output"

**Symptoms:**
- PRD missing sections
- Architecture document lacks diagrams
- Code review has no feedback

**Solution:**
1. Re-run the command with more context
2. Check if you provided sufficient input
3. Verify previous phases completed successfully

**Example:**
```bash
# Instead of:
/jpspec:specify payment system

# Provide more context:
/jpspec:specify payment processing system supporting credit cards, ACH, and crypto,
with PCI DSS compliance requirements from enterprise customers
```

---

### Issue: "Code review flagged too many issues"

**Symptoms:**
- 20+ critical/high priority findings
- Fundamental design flaws identified

**Root Cause:**
- Implementation didn't follow architecture from `/jpspec:plan`
- Requirements from `/jpspec:specify` not met

**Solution:**
1. Review architecture and requirements
2. Re-run `/jpspec:implement` with explicit architecture constraints
3. Consider whether architectural changes are needed

**Prevention:**
- Ensure architecture phase completed before implementation
- Pass architecture outputs explicitly to implementation phase

---

### Issue: "Security scan failed with critical vulnerabilities"

**Symptoms:**
- `/jpspec:validate` blocks release
- Critical CVEs in dependencies
- Code security issues (SQL injection, XSS, etc.)

**Solution:**
1. **Dependency vulnerabilities**: Update dependencies
   ```bash
   npm audit fix
   pip-audit --fix
   ```

2. **Code vulnerabilities**: Review secure-by-design-engineer findings and fix code

3. **Re-run validation**: After fixes, run `/jpspec:validate` again

**Prevention:**
- Run security scans earlier (during implementation)
- Use automated dependency updates (Dependabot, Renovate)

---

### Issue: "Performance tests failing"

**Symptoms:**
- Quality-guardian reports latency > targets
- Throughput below requirements
- Resource usage too high

**Solution:**
1. Review performance requirements from PRD
2. Profile the application to find bottlenecks
3. Apply optimizations:
   - Database query optimization (indexes, query tuning)
   - Caching (Redis, CDN)
   - Code optimization (algorithm improvements)
   - Horizontal scaling (more replicas)

4. Re-run `/jpspec:validate` with updated code

**Example Optimization:**
```go
// Before: N+1 query problem
for _, user := range users {
    orders := db.GetOrdersForUser(user.ID)  // N queries!
}

// After: Single query with JOIN
orders := db.GetOrdersForUsers(userIDs)  // 1 query
```

---

### Issue: "Kubernetes deployment failing"

**Symptoms:**
- Pods in CrashLoopBackOff
- ImagePullBackOff errors
- Resource quota exceeded

**Solution:**

**CrashLoopBackOff:**
```bash
# Check pod logs
kubectl logs <pod-name>

# Check events
kubectl describe pod <pod-name>

# Common causes:
# - Missing environment variables
# - Incorrect startup command
# - Application crashes on startup
```

**ImagePullBackOff:**
```bash
# Verify image exists
docker pull <image-name>

# Check image pull secrets
kubectl get secrets

# Verify registry credentials
```

**Resource Quota Exceeded:**
```bash
# Check namespace quotas
kubectl describe resourcequota

# Reduce resource requests or increase quota
```

---

### Issue: "CI/CD pipeline failing"

**Symptoms:**
- GitHub Actions workflow fails
- Tests pass locally but fail in CI
- Deployment step errors

**Solution:**

**Test failures:**
```yaml
# Add debugging to workflow
- name: Run tests
  run: |
    npm test -- --verbose
    echo "Test results: $?"
```

**Common causes:**
- Environment differences (missing env vars, dependencies)
- Race conditions in tests
- Flaky tests

**Deployment failures:**
- Check credentials/secrets are configured
- Verify Kubernetes context is correct
- Review deployment logs

---

### Issue: "Documentation is unclear or incomplete"

**Symptoms:**
- API docs missing examples
- User guides skip critical steps
- Runbooks lack troubleshooting info

**Solution:**
1. Provide tech-writer agent with more context:
   ```bash
   /jpspec:validate <feature> [include detailed API specs, architecture diagrams, test results]
   ```

2. Request specific documentation sections:
   - API reference with request/response examples
   - Step-by-step tutorials with screenshots
   - Troubleshooting guides with common errors

3. Review and iterate on documentation before final approval

---

### Issue: "Agents working on wrong technology stack"

**Symptoms:**
- Backend-engineer uses Node.js when you wanted Go
- Frontend-engineer uses Vue instead of React
- Wrong database chosen

**Solution:**
1. **Specify technology choices in architecture phase:**
   ```bash
   /jpspec:plan E-commerce platform using Go backend, React frontend, PostgreSQL database
   ```

2. **Document decisions in ADRs:**
   - Architecture phase should create ADRs for key tech choices
   - Pass ADRs to implementation phase

3. **Explicitly constrain in implementation:**
   ```bash
   /jpspec:implement API service in Go using Chi router and PostgreSQL with sqlx
   ```

---

### Issue: "Can't track progress across workflow"

**Symptoms:**
- Losing track of what's been completed
- Multiple iterations blur together
- Hard to reference previous outputs

**Solution:**
1. **Use /speckit artifacts as source of truth:**
   - `/speckit.tasks`: Track specification and task status
   - `/speckit.constitution`: Reference architectural principles

2. **Create a workflow log:**
   ```markdown
   # Project: AI Chatbot
   ## Workflow Log

   2024-01-15: Research complete (Score: 8.5/10 - GO)
   2024-01-16: Specification complete (32 user stories, 87 tasks)
   2024-01-17: Architecture complete (6 ADRs, microservices design)
   2024-01-20: Implementation Phase 1 complete (backend)
   2024-01-22: Implementation Phase 2 complete (frontend)
   2024-01-23: Code review: 3 high priority items addressed
   2024-01-24: Validation in progress...
   ```

3. **Use git branches to track phases:**
   ```bash
   git checkout -b phase/research
   git checkout -b phase/implementation
   git checkout -b phase/validation
   ```

---

### Getting Help

If you encounter issues not covered here:

1. **Review agent outputs carefully** - Often contain helpful error messages and suggestions
2. **Check /speckit artifacts** - May reveal gaps or inconsistencies
3. **Provide more context** - Re-run commands with richer descriptions
4. **Iterate incrementally** - Break complex features into smaller phases

---

## Summary

jpspec transforms software delivery by orchestrating specialized AI agents across the complete lifecycle:

- **Research** validates ideas before investment
- **Specify** creates clear, actionable requirements
- **Plan** designs robust architecture and platform
- **Implement** builds quality code with automatic review
- **Validate** ensures production readiness through QA, security, and docs
- **Operate** establishes SRE-grade operational excellence

**Key Principles:**
- Follow the workflow sequence for best results
- Provide rich context to agents
- Review outputs carefully and iterate as needed
- Address quality gates seriously
- Leverage parallel execution for speed
- Maintain /speckit artifacts for consistency

**Get Started:**
```bash
/jpspec:research <your idea>
```

Build better software, faster, with confidence.
