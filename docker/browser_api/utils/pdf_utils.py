"""
PDF utilities for browser automation.
This module provides functionality for generating PDFs.
"""
import asyncio
import base64
import traceback

class PDFUtils:
    """Utilities for working with PDFs"""
    
    @staticmethod
    async def generate_pdf(page, pdf_options=None) -> str:
        """Generate a PDF of the current page and return as base64 encoded string"""
        try:
            # Default PDF options
            options = {}
            options["format"] = "A4"
            options["print_background"] = True
            options["margin"] = {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
            
            # Supported Playwright PDF parameters
            supported_params = [
                'path', 'scale', 'display_header_footer', 'header_template', 'footer_template',
                'print_background', 'landscape', 'page_ranges', 'format', 'width', 'height',
                'prefer_css_page_size', 'margin'
            ]
            
            # Merge user-provided options but only include supported parameters
            if pdf_options:
                if hasattr(pdf_options, 'items'):
                    for key, value in pdf_options.items():
                        if key in supported_params:
                            options[key] = value
                        else:
                            print(f"Warning: Ignoring unsupported PDF parameter: {key}")
                elif hasattr(pdf_options, '__dict__'):
                    for key, value in pdf_options.__dict__.items():
                        if key in supported_params and not key.startswith('_') and key != '__annotations__':
                            options[key] = value
                        elif key not in ['__annotations__'] and not key.startswith('_'):
                            print(f"Warning: Ignoring unsupported PDF parameter: {key}")
            
            # Wait for any pending requests to complete to ensure full page rendering
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception as network_error:
                print(f"Network idle timeout during PDF generation: {network_error}")
                # Continue anyway, as the page might be usable
                await asyncio.sleep(1)
                
            # Generate PDF with specified options as kwargs
            pdf_bytes = await page.pdf(**options)
            
            # Verify we have actual content
            if not pdf_bytes:
                print("Error: PDF generation failed - no content returned")
                return ""
                
            pdf_size = len(pdf_bytes)
            if pdf_size < 1000:  # Reasonable minimum size for a valid PDF
                print(f"Warning: PDF size suspiciously small ({pdf_size} bytes), may be incomplete")
                if pdf_size < 100:
                    print("Critical: PDF appears to be invalid, content too small")
                    return ""
            else:
                print(f"Successfully generated PDF of {pdf_size} bytes")
                
            return base64.b64encode(pdf_bytes).decode('utf-8')
        except Exception as e:
            print(f"Error generating PDF: {e}")
            traceback.print_exc()
            # Return an empty string rather than failing
            return ""
