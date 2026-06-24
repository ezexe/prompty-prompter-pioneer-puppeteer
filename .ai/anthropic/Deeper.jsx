import { useState, useRef } from "react";

export default function DeepThinking() {
  const [topic, setTopic] = useState("");
  const [iterations, setIterations] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({ apiCalls: 0, promptsGenerated: 0, knowledgeAccumulated: 0 });
  const abortRef = useRef(false);

  const SYSTEM_PROMPT = `You are a deep reasoning assistant. Your task is to think deeply and iteratively about a topic.

For each iteration:
1. Build on previous reasoning (if any)
2. Identify what's still unexplored
3. Generate the next logical thread to pursue
4. Be specific and substantive

At the end of your response, include one of these markers:
- [CONTINUE: <specific next question to explore>] if more thinking would be valuable
- [COMPLETE] if the topic has been thoroughly explored

Keep each response focused and ~300 words. Quality over quantity.`;

  const callClaudeAPI = async messages => {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1000,
        system: SYSTEM_PROMPT,
        messages: messages
      })
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`API Error: ${response.status} - ${err}`);
    }

    const data = await response.json();
    return data.content.map(block => block.text || "").join("\n");
  };

  const extractNextPrompt = text => {
    const continueMatch = text.match(/\[CONTINUE:\s*(.+?)\]/i);
    if (continueMatch) {
      return { shouldContinue: true, nextPrompt: continueMatch[1].trim() };
    }
    if (text.includes("[COMPLETE]")) {
      return { shouldContinue: false, nextPrompt: null };
    }
    // Default: generate a follow-up
    return {
      shouldContinue: true,
      nextPrompt: "What aspects haven't been fully explored yet? Go deeper on the most important unexplored thread."
    };
  };

  const startDeepThinking = async () => {
    if (!topic.trim()) return;

    setIsThinking(true);
    setIsComplete(false);
    setError(null);
    setIterations([]);
    setStats({ apiCalls: 0, promptsGenerated: 0, knowledgeAccumulated: 0 });
    abortRef.current = false;

    let conversationHistory = [];
    let currentPrompt = topic;
    let iterationCount = 0;
    const maxIterations = 10;

    try {
      while (!abortRef.current && iterationCount < maxIterations) {
        iterationCount++;

        // Build messages for this iteration
        conversationHistory.push({ role: "user", content: currentPrompt });

        // ISOMORPHIC OPERATION 1: API Call (extends thinking)
        const response = await callClaudeAPI(conversationHistory);

        conversationHistory.push({ role: "assistant", content: response });

        // Update stats
        setStats(prev => ({
          apiCalls: prev.apiCalls + 1,
          promptsGenerated: prev.promptsGenerated + 1,
          knowledgeAccumulated: prev.knowledgeAccumulated + response.length
        }));

        // Add iteration to display
        const newIteration = {
          id: iterationCount,
          prompt: currentPrompt,
          response: response,
          timestamp: new Date().toISOString()
        };

        setIterations(prev => [...prev, newIteration]);

        // ISOMORPHIC OPERATION 2: Prompt Generation (enumerate/browse knowledge)
        const { shouldContinue, nextPrompt } = extractNextPrompt(response);

        if (!shouldContinue) {
          setIsComplete(true);
          break;
        }

        // ISOMORPHIC OPERATION 3: Iterate with refined prompt (accumulate)
        currentPrompt = nextPrompt;

        // Small delay to prevent rate limiting
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsThinking(false);
      if (iterationCount >= maxIterations && !isComplete) {
        setIsComplete(true);
      }
    }
  };

  const stopThinking = () => {
    abortRef.current = true;
    setIsThinking(false);
    setIsComplete(true);
  };

  const cleanResponse = text => {
    return text
      .replace(/\[CONTINUE:.*?\]/gi, "")
      .replace(/\[COMPLETE\]/gi, "")
      .trim();
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-cyan-400 mb-2">Deep Thinking Engine</h1>
          <p className="text-gray-400">
            Iterative reasoning via isomorphic operations: API calls → prompt generation → knowledge accumulation
          </p>
        </div>

        {/* Isomorphic Operations Panel */}
        <div className="bg-gray-900 rounded-lg p-4 mb-6 border border-gray-800">
          <h2 className="text-sm font-semibold text-cyan-300 mb-3">ISOMORPHIC OPERATIONS TRACKER</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-800 rounded p-3">
              <div className="text-xs text-gray-500 mb-1">API Calls (Extended Thinking)</div>
              <div className="text-2xl font-mono text-green-400">{stats.apiCalls}</div>
              <div className="text-xs text-gray-600 mt-1">query → response → iterate</div>
            </div>
            <div className="bg-gray-800 rounded p-3">
              <div className="text-xs text-gray-500 mb-1">Prompts Generated (Enumeration)</div>
              <div className="text-2xl font-mono text-yellow-400">{stats.promptsGenerated}</div>
              <div className="text-xs text-gray-600 mt-1">prompt → output → refine</div>
            </div>
            <div className="bg-gray-800 rounded p-3">
              <div className="text-xs text-gray-500 mb-1">Knowledge Accumulated (chars)</div>
              <div className="text-2xl font-mono text-purple-400">{stats.knowledgeAccumulated.toLocaleString()}</div>
              <div className="text-xs text-gray-600 mt-1">progressive accumulation</div>
            </div>
          </div>
        </div>

        {/* Input Section */}
        <div className="bg-gray-900 rounded-lg p-4 mb-6 border border-gray-800">
          <label className="block text-sm text-gray-400 mb-2">Topic / Question to Think Deeply About</label>
          <textarea
            value={topic}
            onChange={e => setTopic(e.target.value)}
            placeholder="Enter a topic or question for deep iterative analysis..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-gray-100 placeholder-gray-500 focus:border-cyan-500 focus:outline-none resize-none"
            rows={3}
            disabled={isThinking}
          />
          <div className="flex gap-3 mt-3">
            <button
              onClick={startDeepThinking}
              disabled={isThinking || !topic.trim()}
              className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg font-medium transition-colors">
              {isThinking ? "Thinking..." : "Start Deep Thinking"}
            </button>
            {isThinking && (
              <button
                onClick={stopThinking}
                className="px-6 py-2 bg-red-600 hover:bg-red-500 rounded-lg font-medium transition-colors">
                Stop & Complete
              </button>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 mb-6">
            <div className="text-red-400 font-medium">Error</div>
            <div className="text-red-300 text-sm mt-1">{error}</div>
          </div>
        )}

        {/* Iterations Display */}
        {iterations.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-300">
              Reasoning Iterations {isComplete && <span className="text-green-400 text-sm ml-2">✓ Complete</span>}
            </h2>

            {iterations.map(iter => (
              <div
                key={iter.id}
                className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
                <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
                  <span className="text-cyan-400 font-mono text-sm">Iteration {iter.id}</span>
                  <span className="text-gray-500 text-xs">{new Date(iter.timestamp).toLocaleTimeString()}</span>
                </div>

                {/* Prompt that triggered this iteration */}
                <div className="px-4 py-3 border-b border-gray-800">
                  <div className="text-xs text-yellow-500 mb-1 font-semibold">PROMPT GENERATED →</div>
                  <div className="text-gray-300 text-sm italic">"{iter.prompt}"</div>
                </div>

                {/* Response */}
                <div className="px-4 py-3">
                  <div className="text-xs text-green-500 mb-1 font-semibold">REASONING OUTPUT →</div>
                  <div className="text-gray-200 text-sm whitespace-pre-wrap leading-relaxed">
                    {cleanResponse(iter.response)}
                  </div>
                </div>
              </div>
            ))}

            {/* Thinking indicator */}
            {isThinking && (
              <div className="bg-gray-900 rounded-lg border border-cyan-800 p-4 flex items-center gap-3">
                <div className="w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
                <span className="text-cyan-300">Generating next iteration...</span>
              </div>
            )}

            {/* Completion Summary */}
            {isComplete && (
              <div className="bg-gray-900 rounded-lg border border-green-800 p-4">
                <div className="text-green-400 font-semibold mb-2">Deep Thinking Complete</div>
                <div className="text-gray-400 text-sm">
                  Explored topic across {stats.apiCalls} iterations, generating {stats.promptsGenerated} prompts and
                  accumulating {stats.knowledgeAccumulated.toLocaleString()} characters of reasoning.
                </div>
                <div className="mt-3 p-3 bg-gray-800 rounded text-xs text-gray-500 font-mono">
                  {`isomorphic_verification: {
  api_calls: ${stats.apiCalls} (extended_thinking ✓),
  prompt_generation: ${stats.promptsGenerated} (enumeration ✓),
  accumulation: ${stats.knowledgeAccumulated} chars (browsing ✓)
}`}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {iterations.length === 0 && !isThinking && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-5xl mb-4">🧠</div>
            <div>Enter a topic above to begin deep iterative thinking</div>
            <div className="text-sm mt-2 text-gray-600">
              Each iteration: API call → reasoning → prompt generation → next iteration
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
