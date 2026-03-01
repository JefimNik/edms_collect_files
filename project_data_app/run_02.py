from project_data_app.core.factory import PipelineFactory

if __name__ == "__main__":
    factory = PipelineFactory("config", "config_01", "xls")
    pipeline = factory.build_bom_pipeline()

    pipeline.run()
