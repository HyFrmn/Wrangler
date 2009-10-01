class Job < ActiveRecord::Base
  has_many :tasks

  def status_string
    @status = self[:status]
    if @status == 0:
      return 'waiting'
    elsif @status == 1:
      return 'queued'
    elsif @status == 2:
      return 'running'
    elsif @status == 3:
      return 'finished'
    elsif @status == -3:
      return 'error'
    elsif @status == -2:
      return 'stopped'
    elsif @status == -1:
      return 'paused'
    end
    return self[:status]
  end

  def runtime
    TaskLog.sum(:time, :joins => :task, :conditions => ['tasks.job_id = ?', self[:id]])
  end

  def averagetime
    TaskLog.average(:time, :joins => :task, :conditions => ['tasks.job_id = ? and task_logs.time > 0', self[:id]])
  end
end
