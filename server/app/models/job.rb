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
    return self[:status].to_s
  end

  def runtime
    TaskLog.sum(:time, :joins => :task, :conditions => ['tasks.job_id = ? AND task_logs.time > 0', self[:id]]).to_f
  end

  def averagetime
    TaskLog.average(:time, :joins => :task, :conditions => ['tasks.job_id = ? and task_logs.time > 0', self[:id]]).to_f
  end
  
  def priority
    Task.average(:priority, :conditions => ['job_id = ?', self[:id]]).to_i
  end
  
  def task_count
    Task.count(:conditions => ["job_id = ?", self[:id]]).to_f
  end
  
  def finished
    Task.count(:conditions => ["job_id = ? AND status = 3", self[:id]]).to_f
  end

  def running
    Task.count(:conditions => ["job_id = ? AND status = 2", self[:id]]).to_f
  end

  def queued
    Task.count(:conditions => ["job_id = ? AND status = 1", self[:id]]).to_f
  end

  def waiting
    Task.count(:conditions => ["job_id = ? AND status = 0", self[:id]]).to_f
  end

  def estimate
    self.queued * self.averagetime
  end

  def progress
      (self.finished / self.task_count) * 100
  end
  
end
