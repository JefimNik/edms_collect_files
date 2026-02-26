Project Data Foundation

Modules:

    config/
        config_01.yaml +

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
            ExcelReaderWriter
            PdfExtractor
            PdfBuilder
        StepLoggerService.py
            StepLogger
        database_service.py
            DbManager
        config_manager.py
            ConfigManager +
            (PathResolver)
            (RunContext)
        
    
    common/
        utils.py