class Task < ActiveRecord::Base
  belongs_to :job
  has_many :task_logs
  serialize :env
end
