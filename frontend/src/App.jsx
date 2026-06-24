import { useState } from "react";

import {
  Brain,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Sparkles,
} from "lucide-react";

function App() {

  const [emailText, setEmailText] = useState("");

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const analyzeEmail = async () => {

    if (!emailText) return;

    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: emailText,
          }),
        }
      );

      const data = await response.json();

      setResult(data);

    } catch (error) {

      console.error(error);

    }

    setLoading(false);
  };

  const urgencyColor = () => {

    if (!result) return "";

    if (result.urgency === "High")
      return "text-red-400";

    if (result.urgency === "Medium")
      return "text-yellow-400";

    return "text-green-400";
  };

  return (

    <div className="min-h-screen bg-gradient-to-br from-black via-zinc-950 to-zinc-900 text-white p-8">

      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="mb-10">

          <div className="flex items-center gap-3 mb-3">

            <Brain className="w-10 h-10 text-white" />

            <h1 className="text-5xl font-bold tracking-tight">
              InboxIQ
            </h1>

          </div>

          <p className="text-zinc-400 text-lg">
            AI Email Intelligence Platform
          </p>

        </div>

        {/* Input Box */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 shadow-2xl">

          <textarea
            className="w-full h-72 bg-transparent outline-none text-zinc-200 resize-none text-lg"
            placeholder="Paste your professional email here..."
            value={emailText}
            onChange={(e) => setEmailText(e.target.value)}
          />

          <button
            onClick={analyzeEmail}
            className="mt-4 px-8 py-4 rounded-2xl bg-white text-black font-semibold hover:scale-105 transition duration-300"
          >
            {loading
              ? "Analyzing..."
              : "Analyze Email"}
          </button>

        </div>

        {/* Loading */}
        {loading && (

          <div className="mt-10 text-center">

            <div className="animate-pulse text-zinc-400 text-lg">
              AI is analyzing your email...
            </div>

          </div>
        )}

        {/* Results */}
        {result && (

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-10">

            {/* Summary */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl">

              <div className="flex items-center gap-3 mb-5">

                <FileText className="text-blue-400" />

                <h2 className="text-2xl font-bold">
                  AI Summary
                </h2>

              </div>

              <p className="text-zinc-300 leading-8">
                {result.summary}
              </p>

            </div>

            {/* Sentiment */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl">

              <div className="flex items-center gap-3 mb-5">

                <Sparkles className="text-pink-400" />

                <h2 className="text-2xl font-bold">
                  Sentiment
                </h2>

              </div>

              <p className="text-4xl font-semibold">
                {result.sentiment}
              </p>

            </div>

            {/* Priority */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl">

              <div className="flex items-center gap-3 mb-5">

                <AlertTriangle className="text-yellow-400" />

                <h2 className="text-2xl font-bold">
                  Priority Level
                </h2>

              </div>

              <p className={`text-4xl font-semibold ${urgencyColor()}`}>
                {result.urgency}
              </p>

            </div>

            {/* Action Items */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl">

              <div className="flex items-center gap-3 mb-5">

                <CheckCircle2 className="text-green-400" />

                <h2 className="text-2xl font-bold">
                  Action Items
                </h2>

              </div>

              <ul className="space-y-4">

                {result.action_items.map(
                  (item, index) => (

                    <li
                      key={index}
                      className="text-zinc-300 leading-7"
                    >
                      • {item}
                    </li>
                  )
                )}

              </ul>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}

export default App;