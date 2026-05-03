        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
        }

        header {
            background-color: #e67e50;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .home-icon {
            background-color: white;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 24px;
            text-decoration: none;
            color: #333;
        }

        .search-container {
            flex: 1;
            max-width: 600px;
        }

        .search-box {
            width: 100%;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
        }

        .menu-icon {
            margin-left: auto;
            background-color: #d86f45;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            color: white;
            font-size: 24px;
        }

        .welcome-section {
            padding: 30px 20px;
            background-color: white;
        }

        .welcome-section h1 {
            font-size: 32px;
            color: #333;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .card {
            background-color: white;
            border: 2px solid #333;
            border-radius: 12px;
            padding: 20px;
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }

        .card h2 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }

        .item-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .item-name {
            color: #333;
        }

        .item-link {
            color: #0066cc;
            text-decoration: none;
        }

        .item-link:hover {
            text-decoration: underline;
        }

        .total-cost {
            margin-top: auto;
            padding-top: 15px;
            border-top: 2px solid #333;
            font-weight: bold;
            color: #666;
        }

        .card-content {
            flex: 1;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            header {
                flex-wrap: wrap;
            }
            
            .search-container {
                order: 3;
                width: 100%;
                max-width: none;
            }
        }
