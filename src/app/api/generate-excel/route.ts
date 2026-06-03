import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    // Forward to Python service
    const targetBaseUrl = process.env.PYTHON_SERVICE_URL || process.env.NEXT_PUBLIC_PYTHON_SERVICE_URL || "http://localhost:8000";
    const targetUrl = `${targetBaseUrl}/generate_excel`;
    console.log("[PROXY] Forwarding request to Python service:", targetUrl);

    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
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
    const targetUrl = `${targetBaseUrl}/generate_excel`;
    
    console.error("Error in /api/generate-excel proxy:", {
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
