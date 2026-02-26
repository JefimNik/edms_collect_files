Project Data Foundation

Modules:
    core/
        factory.py
            PipelineFactory
    
    pipelines/
        bom_pipeline.py
            BomPipeline
        pdf_pipeline.py
            PdfPipeline
        estimation_pipeline.py
            EstimationPipeline
    
    services/
        dataframe_service.py
            DfTransformations
            (DfBuilder)
        filesystem_service.py
            FileCollector
            ExcelReadeWriter
            PdfExtractor
            PdfBuilder
        database_service.py
            DbManager
        config_manager.py
            ConfigManager +
            (PathResolver)
            (RunContext)

    
    common/
        utils.py