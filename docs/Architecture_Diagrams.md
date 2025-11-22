# Architecture Diagrams

Visual diagrams for understanding the VUTS system architecture.

## System Overview

```mermaid
graph TD
    A[User Configuration] -->|Topics & Sources| B[Fetching Module]
    B -->|Articles JSON| D[Storage]
    C[Market Module] -->|Market Data JSON| D
    D -->|Articles + Market Data| E[LLM Module]
    E -->|Sentiment Scores JSON| F[Output Results]
    
    style A fill:#e1f5ff
    style B fill:#ffe1f5
    style C fill:#ffe1f5
    style D fill:#f5ffe1
    style E fill:#ffe1f5
    style F fill:#e1f5ff
```

## Data Flow Pipeline

```mermaid
flowchart LR
    subgraph Input
        A[Config File]
        B[API Keys]
    end
    
    subgraph Fetching
        C[News Sources]
        D[Content Extraction]
        E[Save Articles]
    end
    
    subgraph Market
        F[Yahoo Finance]
        G[Calculate Stats]
        H[Save Market Data]
    end
    
    subgraph Analysis
        I[Load Articles]
        J[Load Market Data]
        K[Format Prompt]
        L[Call LLM API]
        M[Parse Response]
        N[Save Scores]
    end
    
    subgraph Output
        O[Score Files]
        P[Aggregation]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    
    A --> F
    F --> G
    G --> H
    
    E --> I
    H --> J
    I --> K
    J --> K
    K --> L
    L --> M
    M --> N
    
    N --> O
    O --> P
```

## Module Dependencies

```mermaid
graph TD
    subgraph Modules
        F[Fetching Module]
        M[Market Module]
        L[LLM Module]
        U[Utils Module]
    end
    
    subgraph External
        API1[News APIs]
        API2[Yahoo Finance]
        API3[OpenAI API]
    end
    
    F -->|uses| U
    M -->|uses| U
    L -->|uses| U
    
    F -->|calls| API1
    M -->|calls| API2
    L -->|calls| API3
    
    F -.reads.-> M
    L -.reads.-> F
    L -.reads.-> M
    
    style U fill:#ffe1e1
    style F fill:#e1f5ff
    style M fill:#e1f5ff
    style L fill:#e1f5ff
```

## Sentiment Analysis Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant LLM as LLM Module
    participant FS as File System
    participant API as OpenAI API
    
    U->>LLM: Run sentiment_analyzer.py
    LLM->>FS: Find article files
    FS-->>LLM: Article list
    
    loop For each article
        LLM->>FS: Read article JSON
        FS-->>LLM: Article content
        
        opt Market context available
            LLM->>FS: Read market data
            FS-->>LLM: Market data
        end
        
        LLM->>LLM: Format prompt
        LLM->>API: Send prompt
        API-->>LLM: Score + Explanation
        LLM->>LLM: Validate score
        LLM->>FS: Save score JSON
    end
    
    LLM-->>U: Complete
```

## File Organization

```mermaid
graph TB
    subgraph Repository
        ROOT[vuts/]
        
        subgraph Documentation
            DOCS[docs/]
            WIKI[wiki/]
        end
        
        subgraph Application
            SCRATCH[scratch/]
            
            subgraph Source
                SRC[src/]
                FETCH[fetching/]
                LLM[llm/]
                MARKET[market/]
                UTILS[utils/]
                TESTS[tests/]
            end
            
            EXAMPLE[example_data/]
            DEMO[demo_workflow.py]
        end
        
        subgraph Output
            OUT[output/]
            ARTICLES[articles/]
            MDATA[market_data/]
            SCORES[llm_scores/]
        end
    end
    
    ROOT --> DOCS
    ROOT --> WIKI
    ROOT --> SCRATCH
    SCRATCH --> SRC
    SRC --> FETCH
    SRC --> LLM
    SRC --> MARKET
    SRC --> UTILS
    SRC --> TESTS
    SCRATCH --> EXAMPLE
    SCRATCH --> DEMO
    SCRATCH --> OUT
    OUT --> ARTICLES
    OUT --> MDATA
    OUT --> SCORES
```

## Score Processing State Machine

```mermaid
stateDiagram-v2
    [*] --> Discovering: Start
    Discovering --> Validating: Articles found
    Validating --> CheckingCache: Valid articles
    CheckingCache --> LoadingMarket: New article
    CheckingCache --> Discovering: Already scored
    LoadingMarket --> FormattingPrompt: Market data loaded
    LoadingMarket --> FormattingPrompt: No market data
    FormattingPrompt --> CallingLLM: Prompt ready
    CallingLLM --> ParsingResponse: Response received
    ParsingResponse --> ValidatingScore: Score extracted
    ValidatingScore --> SavingScore: Valid score
    ValidatingScore --> Discovering: Invalid score
    SavingScore --> Discovering: Score saved
    Discovering --> [*]: All processed
```

## Async Fetching Flow

```mermaid
graph LR
    subgraph Configuration
        CFG[Config File]
        TOPICS[Topics List]
        SOURCES[Sources List]
    end
    
    subgraph Async Tasks
        T1[Task: TSLA + GoogleNews]
        T2[Task: TSLA + BingNews]
        T3[Task: MSFT + GoogleNews]
        T4[Task: MSFT + BingNews]
    end
    
    subgraph Results
        R1[TSLA Articles]
        R2[MSFT Articles]
    end
    
    CFG --> TOPICS
    CFG --> SOURCES
    TOPICS --> T1
    TOPICS --> T2
    TOPICS --> T3
    TOPICS --> T4
    SOURCES --> T1
    SOURCES --> T2
    SOURCES --> T3
    SOURCES --> T4
    
    T1 --> R1
    T2 --> R1
    T3 --> R2
    T4 --> R2
```

## Score Distribution Example

```mermaid
graph TD
    subgraph Sentiment Ranges
        EP[+7 to +10<br/>Extremely Positive]
        VP[+4 to +7<br/>Very Positive]
        MP[+2 to +4<br/>Moderately Positive]
        SP[+0.5 to +2<br/>Slightly Positive]
        N[-0.5 to +0.5<br/>Neutral]
        SN[-2 to -0.5<br/>Slightly Negative]
        MN[-4 to -2<br/>Moderately Negative]
        VN[-7 to -4<br/>Very Negative]
        EN[-10 to -7<br/>Extremely Negative]
    end
    
    subgraph Examples
        E1[Major Breakthrough]
        E2[Earnings Beat]
        E3[Good Results]
        E4[Minor Improvements]
        E5[Balanced Reporting]
        E6[Minor Concerns]
        E7[Warnings]
        E8[Missed Earnings]
        E9[Bankruptcy]
    end
    
    E1 --> EP
    E2 --> VP
    E3 --> MP
    E4 --> SP
    E5 --> N
    E6 --> SN
    E7 --> MN
    E8 --> VN
    E9 --> EN
    
    style EP fill:#00ff00
    style VP fill:#66ff66
    style MP fill:#99ff99
    style SP fill:#ccffcc
    style N fill:#ffff99
    style SN fill:#ffcc99
    style MN fill:#ff9966
    style VN fill:#ff6666
    style EN fill:#ff0000
```

## Utility Module Integration

```mermaid
graph TD
    subgraph Utils
        DT[datetime_utils]
        FU[file_utils]
    end
    
    subgraph Fetching Module
        F1[Parse dates]
        F2[Check recency]
        F3[Save articles]
    end
    
    subgraph LLM Module
        L1[Parse dates]
        L2[Filter articles]
        L3[Save scores]
    end
    
    subgraph Market Module
        M1[Save market data]
        M2[Create directories]
    end
    
    DT --> F1
    DT --> F2
    DT --> L1
    DT --> L2
    
    FU --> F3
    FU --> L3
    FU --> M1
    FU --> M2
    
    style DT fill:#ffe1e1
    style FU fill:#ffe1e1
```

---

## How to Use These Diagrams

These diagrams are written in Mermaid syntax, which renders automatically on GitHub. To view them:

1. **In GitHub**: View this file on GitHub - diagrams render automatically
2. **In VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Online**: Copy the code blocks to https://mermaid.live/

## Diagram Types

- **Graph TD/LR**: Top-down or left-right flow charts
- **Flowchart**: Detailed process flows
- **Sequence Diagram**: Interaction between components
- **State Diagram**: State machines and transitions

## Customizing Diagrams

To modify these diagrams:
1. Edit the Mermaid code blocks
2. Test at https://mermaid.live/
3. Update this file with changes
4. Diagrams will render on GitHub automatically
