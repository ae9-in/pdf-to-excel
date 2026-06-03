"use client";

import React, { useState, useRef, DragEvent } from "react";
import {
  UploadCloud,
  FileSpreadsheet,
  Download,
  AlertCircle,
  Plus,
  Trash2,
  Users,
  ShieldCheck,
  RefreshCw,
  Sparkles,
  Search,
} from "lucide-react";

interface Task {
  id: number;
  name: string;
  team: string;
  taskTitle: string;
  priority: string;
  storyPoints: number;
  dueDate: string;
  description: string;
  email: string;
  status: string;
  completionPct: number;
}

interface ConversionResult {
  sprintTitle: string;
  organisation: string;
  extractedDate: string;
  tasks: Task[];
  rawText: string;
  pageCount: number;
  method: string;
  confidence: number;
}

const TEAMS = [
  "HR",
  "NEW JOINERS",
  "BUSINESS OPERATIONS",
  "PRODUCT",
  "SPOS",
  "SOLID",
  "STUDENT RELATED BUS",
  "SPECIFIC",
];

const PRIORITIES = ["High", "Medium", "Low"];

const STATUSES = ["Not Started", "In Progress", "Completed", "Blocked", "Leave"];

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragActive, setIsDragActive] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Result state
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [downloading, setDownloading] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Drag and Drop handlers
  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      const lowerName = droppedFile.name.toLowerCase();
      if (
        droppedFile.type === "application/pdf" ||
        lowerName.endsWith(".pdf") ||
        lowerName.endsWith(".docx") ||
        lowerName.endsWith(".doc")
      ) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError("Only PDF, DOCX, and DOC files are supported");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const lowerName = selectedFile.name.toLowerCase();
      if (
        selectedFile.type === "application/pdf" ||
        lowerName.endsWith(".pdf") ||
        lowerName.endsWith(".docx") ||
        lowerName.endsWith(".doc")
      ) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError("Only PDF, DOCX, and DOC files are supported");
      }
    }
  };


  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  // Run PDF conversion
  const handleConvert = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    // Simulate multi-step progress for better UX
    setLoadingStep("Uploading document to server...");
    const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

    try {
      const formData = new FormData();
      formData.append("file", file);

      await sleep(600);
      setLoadingStep("Detecting document layout (Text vs Scanned)...");
      await sleep(600);
      setLoadingStep("Extracting text contents (Tesseract OCR if scanned)...");

      const response = await fetch("/api/convert", {
        method: "POST",
        body: formData,
      });

      setLoadingStep("Structuring tasks with local parsing engine...");

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "Failed to convert document");
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error("Backend reported failure");
      }

      setResult({
        sprintTitle: data.summary.sprint_title || "Sprint 1-5",
        organisation: data.summary.organisation || "Akshara Enterprises",
        extractedDate: new Date().toISOString(),
        tasks: data.result.tasks || [],
        rawText: data.result.rawText || "",
        pageCount: data.summary.page_count || 1,
        method: data.summary.method || "text",
        confidence: data.summary.confidence || 0.95,
      });

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: unknown) {
      console.error(err);
      const errMsg = err instanceof Error ? err.message : "An unexpected error occurred during conversion.";
      setError(errMsg);
    } finally {
      setLoading(false);
      setLoadingStep("");
    }
  };

  // Edit task handlers
  const handleTaskChange = (taskId: number, field: keyof Task, value: string | number) => {
    if (!result) return;

    const updatedTasks = result.tasks.map((task) => {
      if (task.id === taskId) {
        const updated = { ...task, [field]: value };
        // Sync status with completionPct automatically if Status is changed to Completed
        if (field === "status" && value === "Completed") {
          updated.completionPct = 100;
        } else if (field === "status" && value === "Not Started") {
          updated.completionPct = 0;
        } else if (field === "status" && value === "Leave") {
          updated.completionPct = 0;
          updated.storyPoints = 0;
          updated.priority = "Low";
          updated.taskTitle = "Leave";
        }
        return updated;
      }
      return task;
    });

    setResult({ ...result, tasks: updatedTasks });
  };

  const handleResultMetadataChange = (field: "sprintTitle" | "organisation", value: string) => {
    if (!result) return;
    setResult({ ...result, [field]: value });
  };

  const handleAddTask = () => {
    if (!result) return;

    const newId = result.tasks.length > 0 ? Math.max(...result.tasks.map((t) => t.id)) + 1 : 1;
    const newTask: Task = {
      id: newId,
      name: "",
      team: TEAMS[0],
      taskTitle: "",
      priority: "Medium",
      storyPoints: 3,
      dueDate: result.tasks[0]?.dueDate || new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "2-digit" }).replace(/ /g, "-"),
      description: "",
      email: "",
      status: "Not Started",
      completionPct: 0,
    };

    setResult({ ...result, tasks: [...result.tasks, newTask] });
  };

  const handleDeleteTask = (taskId: number) => {
    if (!result) return;
    const updatedTasks = result.tasks.filter((t) => t.id !== taskId);
    // Re-index task IDs to maintain consistency
    const reindexed = updatedTasks.map((t, idx) => ({ ...t, id: idx + 1 }));
    setResult({ ...result, tasks: reindexed });
  };

  // Generate and download Excel
  const handleDownload = async () => {
    if (!result) return;

    setDownloading(true);
    setError(null);

    try {
      // Map frontend result back to models.py ConversionResult fields
      const payload = {
        sprintTitle: result.sprintTitle,
        organisation: result.organisation,
        extractedDate: result.extractedDate,
        tasks: result.tasks.map((t) => ({
          id: t.id,
          name: t.name,
          team: t.team,
          taskTitle: t.taskTitle,
          priority: t.priority,
          storyPoints: t.storyPoints,
          dueDate: t.dueDate,
          description: t.description,
          email: t.email,
          status: t.status,
          completionPct: t.completionPct,
        })),
        rawText: result.rawText,
        pageCount: result.pageCount,
        method: result.method,
        confidence: result.confidence,
      };

      const response = await fetch("/api/generate-excel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "Failed to generate Excel sheet");
      }

      const data = await response.json();
      if (!data.success || !data.xlsx_base64) {
        throw new Error("No excel bytes returned from backend");
      }

      // Convert base64 to blob
      const binaryString = window.atob(data.xlsx_base64);
      const charCodes = Array.from(binaryString, (char) => char.charCodeAt(0));
      const bytes = new Uint8Array(charCodes);
      const blob = new Blob([bytes], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      // Trigger browser download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${result.organisation.replace(/\s+/g, "_")}_${result.sprintTitle.replace(/\s+/g, "_")}_converted.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: unknown) {
      console.error(err);
      const errMsg = err instanceof Error ? err.message : "Failed to download Excel file";
      setError(errMsg);
    } finally {
      setDownloading(false);
    }
  };

  const getTeamColor = (team: string) => {
    switch (team.toUpperCase()) {
      case "HR":
        return "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300";
      case "NEW JOINERS":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300";
      case "BUSINESS OPERATIONS":
        return "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300";
      case "PRODUCT":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300";
      case "SPOS":
        return "bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300";
      case "SOLID":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300";
      case "STUDENT RELATED BUS":
        return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300";
      case "SPECIFIC":
        return "bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300";
      default:
        return "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "High":
        return "bg-rose-100 text-rose-800 border border-rose-200 dark:bg-rose-950/30 dark:text-rose-400 dark:border-rose-900/30";
      case "Medium":
        return "bg-amber-100 text-amber-800 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-900/30";
      case "Low":
        return "bg-emerald-100 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/30 dark:text-emerald-400 dark:border-emerald-900/30";
      default:
        return "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Completed":
        return "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-400";
      case "In Progress":
        return "bg-blue-100 text-blue-800 dark:bg-blue-950/30 dark:text-blue-400";
      case "Blocked":
        return "bg-rose-100 text-rose-800 dark:bg-rose-950/30 dark:text-rose-400";
      case "Leave":
        return "bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400 italic";
      default:
        return "bg-amber-100 text-amber-800 dark:bg-amber-950/30 dark:text-amber-400";
    }
  };

  const filteredTasks = result
    ? result.tasks.filter(
        (task) =>
          task.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          task.team.toLowerCase().includes(searchQuery.toLowerCase()) ||
          task.taskTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
          task.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans antialiased selection:bg-indigo-500 selection:text-white pb-16">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/60 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <FileSpreadsheet className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                EarlyBird India
              </h1>
              <p className="text-[10px] text-slate-400 font-medium">
                DOCUMENT → BEAUTIFUL EXCEL CONVERTER
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold tracking-wider uppercase text-slate-400">
              Dev Engine Active
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 mt-10">
        {success && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm flex items-center gap-3 animate-fade-in">
            <ShieldCheck className="h-5 w-5 text-emerald-400 shrink-0" />
            <div>
              <span className="font-semibold">Success! </span>
              <span>Document analyzed and tasks extracted successfully.</span>
            </div>
          </div>
        )}

        {/* Upload Panel */}
        {!result && (
          <div className="max-w-xl mx-auto animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-extrabold tracking-tight text-white mb-2">
                Convert Sprint Tasks Instantly
              </h2>
              <p className="text-slate-400">
                Upload your raw task allocation PDF or Word document (.docx/.doc). Our engine extracts people,
                sprints, and tasks using a secure offline parsing engine and builds structured, formula-driven
                sprint Excel dashboards.
              </p>
            </div>

            {/* Drop Zone */}
            <div
              className={`relative rounded-2xl border-2 border-dashed p-10 text-center cursor-pointer transition-all duration-300 ${
                isDragActive
                  ? "border-indigo-400 bg-indigo-500/5 shadow-2xl shadow-indigo-500/5 animate-pulse-border"
                  : "border-slate-700 bg-slate-950/40 hover:border-slate-600 hover:bg-slate-950/60"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={triggerFileInput}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
              />
              <div className="flex flex-col items-center justify-center gap-4">
                <div className="h-16 w-16 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 transition-transform group-hover:scale-105">
                  <UploadCloud className="h-8 w-8" />
                </div>
                <div>
                  <p className="font-semibold text-white text-base">
                    {file ? file.name : "Drag & Drop PDF or Word document"}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    {file
                      ? `${(file.size / 1024 / 1024).toFixed(2)} MB`
                      : "or click to browse from explorer"}
                  </p>
                </div>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-start gap-3">
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {file && !loading && (
              <button
                onClick={handleConvert}
                className="w-full mt-6 py-3.5 px-6 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white font-semibold transition-all duration-200 shadow-lg shadow-indigo-500/25 active:scale-[0.99] flex items-center justify-center gap-2 group"
              >
                <Sparkles className="h-5 w-5 text-indigo-200 group-hover:animate-bounce" />
                Analyze & Extract Tasks
              </button>
            )}

            {loading && (
              <div className="mt-8 text-center p-6 rounded-2xl bg-slate-950/30 border border-slate-800">
                <div className="relative h-12 w-12 mx-auto mb-4">
                  <div className="absolute inset-0 rounded-full border-4 border-indigo-500/20" />
                  <div className="absolute inset-0 rounded-full border-4 border-t-indigo-400 animate-spin" />
                </div>
                <p className="font-medium text-white text-sm">{loadingStep}</p>
                <p className="text-xs text-slate-400 mt-2">
                  This can take up to 20-30 seconds depending on OCR status
                </p>
              </div>
            )}
          </div>
        )}

        {/* Dashboard/Table View */}
        {result && (
          <div className="animate-fade-in space-y-8">
            {/* Header Metadata */}
            <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              <div className="space-y-2 w-full md:w-auto">
                <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs tracking-wider uppercase">
                  <Sparkles className="h-3.5 w-3.5" /> Ready for Customization
                </div>
                <div className="flex flex-col sm:flex-row gap-4">
                  <div>
                    <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                      Organisation
                    </label>
                    <input
                      type="text"
                      value={result.organisation}
                      onChange={(e) =>
                        handleResultMetadataChange("organisation", e.target.value)
                      }
                      className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm font-semibold text-white focus:outline-none focus:border-indigo-500 w-full sm:w-64"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                      Sprint / Date Title
                    </label>
                    <input
                      type="text"
                      value={result.sprintTitle}
                      onChange={(e) =>
                        handleResultMetadataChange("sprintTitle", e.target.value)
                      }
                      className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm font-semibold text-white focus:outline-none focus:border-indigo-500 w-full sm:w-80"
                    />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-3 items-center w-full md:w-auto">
                <button
                  onClick={() => {
                    setResult(null);
                    setFile(null);
                  }}
                  className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-950/40 hover:bg-slate-950 text-slate-300 font-semibold text-sm transition-all"
                >
                  Clear Upload
                </button>
                <button
                  onClick={handleDownload}
                  disabled={downloading}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white font-semibold text-sm transition-all flex items-center gap-2 shadow-lg shadow-indigo-500/20 active:scale-[0.98] disabled:opacity-50"
                >
                  {downloading ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      Generating styled sheet...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4" />
                      Download Styled Excel
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Metric KPI cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass-panel p-5 rounded-2xl flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                  <FileSpreadsheet className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-slate-400 text-xs font-medium">Total Tasks</p>
                  <p className="text-2xl font-bold text-white mt-0.5">
                    {result.tasks.length}
                  </p>
                </div>
              </div>

              <div className="glass-panel p-5 rounded-2xl flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-400">
                  <AlertCircle className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-slate-400 text-xs font-medium">High Priority</p>
                  <p className="text-2xl font-bold text-white mt-0.5">
                    {result.tasks.filter((t) => t.priority === "High").length}
                  </p>
                </div>
              </div>

              <div className="glass-panel p-5 rounded-2xl flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                  <ShieldCheck className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-slate-400 text-xs font-medium">Completed</p>
                  <p className="text-2xl font-bold text-white mt-0.5">
                    {result.tasks.filter((t) => t.status === "Completed").length}
                  </p>
                </div>
              </div>

              <div className="glass-panel p-5 rounded-2xl flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
                  <Users className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-slate-400 text-xs font-medium">Extraction Confidence</p>
                  <p className="text-2xl font-bold text-white mt-0.5">
                    {(result.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Error notifications */}
            {error && (
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-start gap-3">
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Table & Editor Section */}
            <div className="glass-panel rounded-2xl overflow-hidden">
              <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h3 className="font-bold text-lg text-white">Sprint Tasks</h3>
                  <p className="text-xs text-slate-400">
                    Verify and edit task details below. All adjustments are compiled
                    dynamically into Excel formulas.
                  </p>
                </div>
                <div className="flex gap-3 items-center w-full sm:w-auto">
                  <div className="relative w-full sm:w-64">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search tasks..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="bg-slate-900/60 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 w-full"
                    />
                  </div>
                  <button
                    onClick={handleAddTask}
                    className="h-9 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition-all flex items-center gap-1.5 shrink-0"
                  >
                    <Plus className="h-3.5 w-3.5" /> Add Task
                  </button>
                </div>
              </div>

              {/* Table Wrapper */}
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-sm table-fixed min-w-[1920px]">
                  <thead>
                    <tr className="bg-slate-950/40 border-b border-slate-800 text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                      <th className="py-4 px-4 text-center w-[50px]">#</th>
                      <th className="py-4 px-4 w-[160px]">Name</th>
                      <th className="py-4 px-4 w-[190px]">Team</th>
                      <th className="py-4 px-4 w-[190px]">Task Title</th>
                      <th className="py-4 px-4 w-[110px]">Priority</th>
                      <th className="py-4 px-4 w-[100px] text-center">SP</th>
                      <th className="py-4 px-4 w-[110px]">Due Date</th>
                      <th className="py-4 px-4 w-[600px]">Description</th>
                      <th className="py-4 px-4 w-[200px]">Email</th>
                      <th className="py-4 px-4 w-[120px]">Status</th>
                      <th className="py-4 px-4 w-[90px] text-center">Done %</th>
                      <th className="py-4 px-4 text-center w-[70px]">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredTasks.length === 0 ? (
                      <tr>
                        <td colSpan={12} className="py-8 text-center text-slate-500">
                          No tasks match your search query.
                        </td>
                      </tr>
                    ) : (
                      filteredTasks.map((task, rowIdx) => (
                        <tr
                          key={`task-${task.id}-${rowIdx}`}
                          className="hover:bg-slate-800/10 transition-colors"
                        >
                          {/* ID */}
                          <td className="py-3 px-4 text-center text-slate-500 font-mono text-xs">
                            {task.id}
                          </td>

                          {/* Owner Name */}
                          <td className="py-3 px-4">
                            <input
                              type="text"
                              value={task.name}
                              onChange={(e) =>
                                handleTaskChange(task.id, "name", e.target.value)
                              }
                              className="bg-transparent hover:bg-slate-800/30 focus:bg-slate-950 focus:outline-none focus:border-indigo-500 border border-transparent rounded px-2 py-1 text-white font-medium w-full text-xs"
                            />
                          </td>

                          {/* Team */}
                          <td className="py-3 px-4">
                            <select
                              value={task.team}
                              onChange={(e) =>
                                handleTaskChange(task.id, "team", e.target.value)
                              }
                              className={`bg-slate-900 border border-slate-700 rounded px-2 py-1.5 text-xs font-semibold focus:outline-none focus:border-indigo-500 w-full ${getTeamColor(
                                task.team
                              )}`}
                            >
                              {TEAMS.map((t) => (
                                <option key={t} value={t} className="bg-slate-900 text-white">
                                  {t}
                                </option>
                              ))}
                            </select>
                          </td>

                          {/* Task Title */}
                          <td className="py-3 px-4">
                            <input
                              type="text"
                              value={task.taskTitle}
                              onChange={(e) =>
                                handleTaskChange(task.id, "taskTitle", e.target.value)
                              }
                              className="bg-transparent hover:bg-slate-800/30 focus:bg-slate-950 focus:outline-none focus:border-indigo-500 border border-transparent rounded px-2 py-1 text-white font-semibold w-full text-xs"
                            />
                          </td>

                          {/* Priority */}
                          <td className="py-3 px-4">
                            <select
                              value={task.priority}
                              onChange={(e) =>
                                handleTaskChange(task.id, "priority", e.target.value)
                              }
                              className={`border border-transparent rounded px-2 py-1.5 text-xs font-semibold focus:outline-none w-full text-center ${getPriorityColor(
                                task.priority
                              )}`}
                            >
                              {PRIORITIES.map((p) => (
                                <option key={p} value={p} className="bg-slate-900 text-white font-normal">
                                  {p}
                                </option>
                              ))}
                            </select>
                          </td>

                          {/* Story Points */}
                          <td className="py-3 px-4">
                            <input
                              type="number"
                              min="0"
                              max="13"
                              value={task.storyPoints}
                              onChange={(e) =>
                                handleTaskChange(
                                  task.id,
                                  "storyPoints",
                                  parseInt(e.target.value) || 0
                                )
                              }
                              className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-center text-xs text-white focus:outline-none w-full font-mono"
                            />
                          </td>

                          {/* Due Date */}
                          <td className="py-3 px-4">
                            <input
                              type="text"
                              value={task.dueDate}
                              onChange={(e) =>
                                handleTaskChange(task.id, "dueDate", e.target.value)
                              }
                              className="bg-transparent hover:bg-slate-800/30 focus:bg-slate-950 focus:outline-none focus:border-indigo-500 border border-transparent rounded px-2 py-1 text-white text-xs w-full font-mono"
                            />
                          </td>

                          {/* Description */}
                          <td className="py-3 px-4">
                            <textarea
                              value={task.description}
                              rows={2}
                              onChange={(e) =>
                                handleTaskChange(task.id, "description", e.target.value)
                              }
                              className="bg-transparent hover:bg-slate-800/30 focus:bg-slate-950 focus:outline-none focus:border-indigo-500 border border-transparent rounded px-2 py-1 text-slate-300 text-xs w-full resize-y min-h-[2.75rem] leading-relaxed"
                            />
                          </td>

                          {/* Email */}
                          <td className="py-3 px-4">
                            <input
                              type="email"
                              value={task.email}
                              onChange={(e) =>
                                handleTaskChange(task.id, "email", e.target.value)
                              }
                              className="bg-transparent hover:bg-slate-800/30 focus:bg-slate-950 focus:outline-none focus:border-indigo-500 border border-transparent rounded px-2 py-1 text-slate-300 text-xs w-full"
                            />
                          </td>

                          {/* Status */}
                          <td className="py-3 px-4">
                            <select
                              value={task.status}
                              onChange={(e) =>
                                handleTaskChange(task.id, "status", e.target.value)
                              }
                              className={`border border-transparent rounded px-2 py-1.5 text-xs font-semibold focus:outline-none w-full text-center ${getStatusColor(
                                task.status
                              )}`}
                            >
                              {STATUSES.map((s) => (
                                <option key={s} value={s} className="bg-slate-900 text-white font-normal">
                                  {s}
                                </option>
                              ))}
                            </select>
                          </td>

                          {/* Done % */}
                          <td className="py-3 px-4">
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={task.completionPct}
                              onChange={(e) =>
                                handleTaskChange(
                                  task.id,
                                  "completionPct",
                                  parseInt(e.target.value) || 0
                                )
                              }
                              className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-center text-xs text-white focus:outline-none w-full font-mono"
                            />
                          </td>

                          {/* Delete */}
                          <td className="py-3 px-4 text-center">
                            <button
                              onClick={() => handleDeleteTask(task.id)}
                              className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
                              title="Delete Task"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
