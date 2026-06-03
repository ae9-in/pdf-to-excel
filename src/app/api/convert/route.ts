import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    // Forward to Python service
    const targetBaseUrl = process.env.PYTHON_SERVICE_URL || process.env.NEXT_PUBLIC_PYTHON_SERVICE_URL || "http://localhost:8000";
    const targetUrl = `${targetBaseUrl}/convert`;
    console.log("[PROXY] Forwarding request to Python service:", targetUrl);
    
    const backendFormData = new FormData();
    backendFormData.append("file", file);

    const response = await fetch(targetUrl, {
      method: "POST",
      body: backendFormData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { 
          error: `Backend service error: ${errorText || response.statusText}`,
          targetUrl: targetUrl
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    const errorMessage = error?.message || String(error);
    const cause = error?.cause ? (error.cause.message || String(error.cause)) : null;
    const systemCode = error?.cause?.code || error?.code || null;
    const targetBaseUrl = process.env.PYTHON_SERVICE_URL || process.env.NEXT_PUBLIC_PYTHON_SERVICE_URL || "http://localhost:8000";
    const targetUrl = `${targetBaseUrl}/convert`;
    
    console.error("Error in /api/convert proxy:", {
      message: errorMessage,
      cause: cause,
      code: systemCode,
      targetUrl: targetUrl
    });

    return NextResponse.json(
      { 
        error: `Internal server error: ${errorMessage}`,
        cause: cause,
        code: systemCode,
        targetUrl: targetUrl
      },
      { status: 500 }
    );
  }
}
